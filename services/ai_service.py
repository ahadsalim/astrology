import logging
from openai import OpenAI
from config import Config

logger = logging.getLogger(__name__)


class AIService:
    """Handles AI API interactions"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(
            base_url=Config.API_URL,
            api_key=Config.API_KEY
        )
    
    def generate_analysis(self, prompt, model=None):
        """
        Generate AI analysis
        
        Args:
            prompt: The prompt to send to AI
            model: Model name (defaults to ASTRO_MODEL from config)
            
        Returns:
            AI generated text
        """
        if model is None:
            model = Config.ASTRO_MODEL
        
        try:
            logger.info(f"Calling AI with model: {model}")
            logger.info(f"Prompt length: {len(prompt)} characters")
            
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                timeout=600  # 10 minute timeout - API is slow
            )
            
            result = completion.choices[0].message.content
            logger.info(f"AI response received successfully. Length: {len(result)} characters")
            return result
            
        except Exception as e:
            logger.error(f"AI API error: {e}")
            raise RuntimeError(f"خطا در ارتباط با هوش مصنوعی: {str(e)}")
    
    def simplify_text(self, text):
        """
        Simplify astrological text
        
        Args:
            text: Complex astrological text
            
        Returns:
            Simplified version
        """
        prompt = f"""
متن زیر یک تحلیل نجومی است.
تمام اصطلاحات تخصصی نجومی را حذف کن و آن را به یک متن ساده و روان تبدیل کن
که هر فرد عادی بتواند بفهمد.
از دادن پیشنهاد در انتها خودداری کن. متن باید مانند یک گزارش برای مخاطب باشد.
در ابتدا یک خط توضیح بده که این گزارش چیست و سپس متن ساده شده را بنویس.
خروجی بصورت کد HTML باشد.

{text}
"""
        
        return self.generate_analysis(prompt, model=Config.SIMPLIFY_MODEL)
