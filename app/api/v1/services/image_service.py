import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from typing import List
from app.core.config import settings
from app.api.v1.models.country import Country

class ImageService:
    """Service for generating summary images"""
    
    IMAGE_FILENAME = "summary.png"
    
    @staticmethod
    def get_image_path() -> str:
        """Get full path to summary image"""
        return os.path.join(settings.cache_path, ImageService.IMAGE_FILENAME)
    
    @staticmethod
    def image_exists() -> bool:
        """Check if summary image exists"""
        return os.path.exists(ImageService.get_image_path())
    
    @staticmethod
    def generate_summary_image(
        total_countries: int,
        top_countries: List[Country],
        last_refreshed: datetime
    ) -> str:
        """
        Generate summary image with country statistics
        
        Args:
            total_countries: Total number of countries
            top_countries: Top 5 countries by GDP
            last_refreshed: Timestamp of last refresh
            
        Returns: Path to generated image
        """
        # Image dimensions
        width = 800
        height = 600
        
        # Colors
        bg_color = (255, 255, 255)
        text_color = (0, 0, 0)
        header_color = (25, 118, 210)
        line_color = (200, 200, 200)
        
        # Create image
        image = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Try to use a nicer font, fallback to default
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
        
        # Draw title
        title = "Country Currency Summary"
        draw.text((50, 40), title, fill=header_color, font=title_font)
        
        # Draw horizontal line
        draw.line([(50, 90), (width - 50, 90)], fill=line_color, width=2)
        
        # Draw total countries
        y_pos = 120
        draw.text((50, y_pos), f"Total Countries: {total_countries}", fill=text_color, font=header_font)
        
        # Draw last refreshed timestamp
        y_pos += 40
        refresh_time = last_refreshed.strftime("%Y-%m-%d %H:%M:%S UTC") if last_refreshed else "Never"
        draw.text((50, y_pos), f"Last Refreshed: {refresh_time}", fill=text_color, font=body_font)
        
        # Draw horizontal line
        y_pos += 40
        draw.line([(50, y_pos), (width - 50, y_pos)], fill=line_color, width=2)
        
        # Draw top 5 countries header
        y_pos += 30
        draw.text((50, y_pos), "Top 5 Countries by Estimated GDP:", fill=header_color, font=header_font)
        
        # Draw top countries
        y_pos += 40
        for idx, country in enumerate(top_countries, 1):
            if country.estimated_gdp:
                gdp_formatted = f"${country.estimated_gdp:,.2f}"
            else:
                gdp_formatted = "N/A"
            
            text = f"{idx}. {country.name} - {gdp_formatted}"
            draw.text((70, y_pos), text, fill=text_color, font=body_font)
            y_pos += 35
        
        # Save image
        image_path = ImageService.get_image_path()
        image.save(image_path)
        
        return image_path