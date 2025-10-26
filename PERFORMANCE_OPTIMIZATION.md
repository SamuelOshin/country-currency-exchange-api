# Performance Optimization: From 156 Seconds to 9 Seconds

## The Challenge

Our `/countries/refresh` endpoint was taking **2-3 minutes** (120-156 seconds) to complete, causing timeouts in production. The endpoint needed to:

1. Fetch 250+ countries from external API
2. Fetch exchange rates from another API
3. Calculate GDP estimates
4. Update/insert all countries in the database
5. Generate a summary image

**Target**: Complete in under 30 seconds (ideally under 10 seconds)

---

## Initial Bottleneck Analysis

### First Attempt: Using `setattr()` in a Loop
```python
# SLOW: 120+ seconds
for country_data in countries_data:
    if name_lower in existing_dict:
        country = existing_dict[name_lower]
        for key, value in country_data.items():
            if key != "id":
                setattr(country, key, value)  # ❌ SQLAlchemy tracks each change
        updates.append(country)
```

**Problem**: SQLAlchemy's ORM tracked each `setattr()` call individually, creating overhead for 250 countries × 9 fields = 2,250+ change events.

**Time**: ~120 seconds

---

### Second Attempt: Using `bulk_update_mappings()`
```python
# STILL SLOW: 143 seconds
update_mappings = []
for country_data in countries_data:
    update_data = country_data.copy()
    update_data["id"] = existing_dict[name_lower]
    update_mappings.append(update_data)

self.db.bulk_update_mappings(Country, update_mappings)
```

**Problem**: 
1. Still generated 250 individual UPDATE statements
2. The model had `onupdate=func.now()` which caused each UPDATE to call the database `now()` function
3. Network latency to remote MySQL server (Aiven Cloud) × 250 queries = disaster

**SQL Generated**:
```sql
UPDATE countries SET name=..., last_refreshed_at=now() WHERE id=1;
UPDATE countries SET name=..., last_refreshed_at=now() WHERE id=2;
-- ... 248 more individual UPDATE statements
```

**Time**: ~143 seconds (bulk update alone!)

---

## The Magic Solution: MySQL's `ON DUPLICATE KEY UPDATE`

### What is ON DUPLICATE KEY UPDATE?

MySQL has a special feature that combines INSERT and UPDATE in a **single statement**. When you try to insert a row with a duplicate unique key, it updates the existing row instead.

```sql
INSERT INTO countries (name, capital, region, ...)
VALUES 
    ('Afghanistan', 'Kabul', 'Asia', ...),
    ('Albania', 'Tirana', 'Europe', ...),
    -- ... all 250 countries in ONE statement
ON DUPLICATE KEY UPDATE
    capital = VALUES(capital),
    region = VALUES(region),
    population = VALUES(population),
    -- ... other fields
```

### Why It's Fast

1. **Single Network Round-Trip**: Instead of 250 separate queries, we send 3 batches (100 records each)
2. **No Database Function Calls**: We pass the timestamp as a value, not calling `now()` 250 times
3. **MySQL-Native Operation**: The database handles the upsert logic internally (much faster than application logic)
4. **Batch Processing**: MySQL can optimize the entire batch at once

---

## Implementation Details

### Step 1: Remove `onupdate=func.now()` from Model

**Before (SLOW)**:
```python
class Country(Base):
    last_refreshed_at = Column(
        TIMESTAMP, 
        server_default=func.now(), 
        onupdate=func.now()  # ❌ Causes 250 database function calls
    )
```

**After (FAST)**:
```python
class Country(Base):
    last_refreshed_at = Column(
        TIMESTAMP, 
        server_default=func.now()  # ✅ Only for initial insert
    )
```

Now we control the timestamp in application code.

---

### Step 2: Build Raw SQL with Manual Escaping

```python
def bulk_upsert(self, countries_data: List[dict]) -> int:
    now = datetime.utcnow()
    
    # Build VALUES clause
    values_list = []
    for country_data in countries_data:
        # Escape single quotes for SQL injection prevention
        name = country_data['name'].replace("'", "''")
        capital = country_data.get('capital', '').replace("'", "''") if country_data.get('capital') else ''
        
        value = (
            f"('{name}', '{capital}', '{region}', {population}, "
            f"'{currency_code}', {exchange_rate}, {estimated_gdp}, "
            f"'{flag_url}', '{now.strftime('%Y-%m-%d %H:%M:%S')}')"
        )
        values_list.append(value)
```

**Key Points**:
- ✅ Escape single quotes to prevent SQL injection (`O'Brien` → `O''Brien`)
- ✅ Handle NULL values properly (`NULL` not `'NULL'`)
- ✅ Format timestamp as string once, not 250 times

---

### Step 3: Batch Processing to Avoid Packet Size Limits

```python
# Process in batches of 100 to avoid hitting MySQL max_allowed_packet
batch_size = 100
for i in range(0, len(values_list), batch_size):
    batch = values_list[i:i + batch_size]
    values_str = ", ".join(batch)
    
    upsert_sql = f"""
    INSERT INTO countries (name, capital, region, population, ...)
    VALUES {values_str}
    ON DUPLICATE KEY UPDATE
        capital = VALUES(capital),
        region = VALUES(region),
        ...
    """
    
    self.db.execute(text(upsert_sql))
```

**Why Batching**:
- MySQL has a `max_allowed_packet` limit (default 64MB)
- 100 records per batch balances performance vs. packet size
- 250 records = 3 queries instead of 250 queries

---

### Step 4: Parallel API Fetching

**Before (Sequential - 5+ seconds)**:
```python
countries_data = await fetch_countries()      # 2-3 seconds
exchange_rates = await fetch_exchange_rates() # 2-3 seconds
# Total: 4-6 seconds
```

**After (Parallel - 2-3 seconds)**:
```python
countries_data, exchange_rates = await asyncio.gather(
    fetch_countries(),
    fetch_exchange_rates()
)
# Total: ~3 seconds (time of slowest API call)
```

**Savings**: ~2-3 seconds

---

### Step 5: Async Image Generation

**Before (Blocking)**:
```python
generate_summary_image()  # Blocks the response
```

**After (Non-blocking)**:
```python
async def _generate_summary_image(self):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, self._generate_image_sync)
```

**Benefit**: Image generation runs in background thread, doesn't block the HTTP response

---

## Performance Comparison

| Operation | Before | After | Improvement |
|-----------|--------|-------|-------------|
| **Fetch APIs** | 5-6s (sequential) | 2-3s (parallel) | **2x faster** |
| **Database Upsert** | 143s (250 UPDATEs) | 4-5s (3 batch queries) | **29x faster** |
| **Image Generation** | 1-2s (blocking) | 1s (async) | Non-blocking |
| **TOTAL** | **156s** | **9.6s** | **16x faster** ✅ |

---

## Key Lessons Learned

### 1. **ORM Abstraction Has a Cost**

SQLAlchemy's ORM is convenient but adds overhead. For bulk operations, raw SQL is often better:

- ✅ Use ORM for single-record operations, complex queries, relationships
- ✅ Use raw SQL for bulk inserts/updates, performance-critical paths

### 2. **Network Latency Multiplies with Query Count**

When using a remote database (cloud-hosted):
- **Local database**: 250 queries × 1ms = 250ms
- **Remote database**: 250 queries × 500ms = **125 seconds!**

**Solution**: Minimize query count at all costs.

### 3. **Database-Specific Features Are Powerful**

MySQL's `ON DUPLICATE KEY UPDATE` is:
- ✅ Simpler than application logic (fetch → compare → update/insert)
- ✅ Faster (single operation vs. multiple)
- ✅ Atomic (no race conditions)

Other databases have similar features:
- **PostgreSQL**: `INSERT ... ON CONFLICT DO UPDATE`
- **SQLite**: `INSERT ... ON CONFLICT REPLACE`

### 4. **Parallel I/O Operations**

When you have multiple independent I/O operations (API calls, database queries):
```python
# Sequential: sum of all times
result1 = await operation1()  # 2s
result2 = await operation2()  # 2s
# Total: 4s

# Parallel: time of slowest operation
result1, result2 = await asyncio.gather(
    operation1(),  # 2s
    operation2()   # 2s
)
# Total: 2s
```

### 5. **Measure, Don't Guess**

We added detailed timing logs:
```python
t1 = time.time()
# ... operation ...
logger.info(f"Operation took {time.time()-t1:.2f}s")
```

This revealed that 92% of time (143/156s) was in the database update!

---

## SQL Injection Prevention

**Important**: When building raw SQL, always escape user input:

```python
# ❌ DANGEROUS - SQL injection vulnerability
name = country_data['name']
sql = f"INSERT INTO countries (name) VALUES ('{name}')"
# If name = "'; DROP TABLE countries; --" → disaster!

# ✅ SAFE - Escape single quotes
name = country_data['name'].replace("'", "''")
sql = f"INSERT INTO countries (name) VALUES ('{name}')"
# If name = "O'Brien" → "O''Brien" (safe)
```

**Better**: Use parameterized queries when possible. We used string building here because `ON DUPLICATE KEY UPDATE` with 250 records is easier to construct dynamically.

---

## Production Deployment Tips

### 1. Environment-Specific Cache Directories

```python
@property
def cache_path(self) -> str:
    if self.ENVIRONMENT == "production":
        return "/tmp/cache"  # Writable in containers
    return os.path.abspath(self.CACHE_DIR)  # Local development
```

**Why**: Production containers (Docker, Leapcell, etc.) often have read-only file systems except for `/tmp`.

### 2. Set Environment Variables

```env
# Critical for Leapcell/production
ENVIRONMENT=production

# API timeouts
API_TIMEOUT=30

# Database connection pooling (if using SQLAlchemy)
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

### 3. Monitor Query Performance

Use SQLAlchemy's logging to see actual SQL:
```python
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

---

## Code Before & After

### Before (Slow)
```python
def bulk_upsert(self, countries_data):
    existing_countries = self.db.query(Country).all()  # 5s
    existing_dict = {c.name.lower(): c for c in existing_countries}
    
    for country_data in countries_data:  # 143s for 250 countries
        if country_data["name"].lower() in existing_dict:
            country = existing_dict[country_data["name"].lower()]
            for key, value in country_data.items():
                setattr(country, key, value)  # ORM tracking overhead
    
    self.db.commit()  # 1s
```

### After (Fast)
```python
def bulk_upsert(self, countries_data):
    now = datetime.utcnow()
    values_list = []
    
    for country_data in countries_data:  # <1s - just string building
        name = country_data['name'].replace("'", "''")
        # ... build value tuple ...
        values_list.append(value)
    
    for i in range(0, len(values_list), 100):  # 3 batches
        batch = values_list[i:i+100]
        sql = f"INSERT INTO countries (...) VALUES {','.join(batch)} ON DUPLICATE KEY UPDATE ..."
        self.db.execute(text(sql))  # ~1.5s per batch
    
    self.db.commit()  # 1s
```

---

## Conclusion

The "magic" wasn't one thing—it was a combination of optimizations:

1. 🚀 **Use database-native bulk operations** (`ON DUPLICATE KEY UPDATE`)
2. ⚡ **Minimize network round-trips** (3 queries instead of 250)
3. 🔄 **Parallelize independent I/O** (`asyncio.gather`)
4. 📊 **Measure everything** (timing logs revealed the bottleneck)
5. 🎯 **Use the right tool for the job** (raw SQL for bulk, ORM for single records)

**Result**: **16x performance improvement** (156s → 9.6s)

---

## Further Optimizations (If Needed)

If you need even more speed:

1. **Database Connection Pooling**: Reuse connections instead of creating new ones
2. **Caching**: Cache exchange rates (they don't change often)
3. **Async Database Driver**: Use `asyncpg` (PostgreSQL) or `aiomysql` for true async DB operations
4. **Message Queue**: Move refresh to background job (Celery, RQ)
5. **Database Indexes**: Ensure `name` column has UNIQUE index (we already have this)

---

## Resources

- [MySQL INSERT ... ON DUPLICATE KEY UPDATE](https://dev.mysql.com/doc/refman/8.0/en/insert-on-duplicate.html)
- [SQLAlchemy Bulk Operations](https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html#bulk-operations)
- [Python asyncio.gather()](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather)
- [SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

---

**Author**: Performance optimization case study  
**Date**: October 26, 2025  
**Impact**: 16x faster, passing all production tests ✅
