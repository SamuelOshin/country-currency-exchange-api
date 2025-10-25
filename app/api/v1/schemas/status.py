from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class StatusResponse(BaseModel):
    total_countries: int
    last_refreshed_at: Optional[datetime] = None