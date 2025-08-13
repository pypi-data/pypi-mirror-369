import re
import time
import requests
import warnings
import pdfplumber
from io import BytesIO
from typing import Optional
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

class CBEVerifier:
    CBE_URL = "https://apps.cbe.com.et:100/?id={reference}{suffix}"
    MAX_RETRIES = 5
    RETRY_DELAY = 2  # seconds
    
    def __init__(self, verify_ssl: bool = False):
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
    
    def verify(self, reference: str, account_suffix: str) -> dict:
        if not self._validate_inputs(reference, account_suffix):
            return {"success": False, "error": "Invalid input parameters"}
            
        for attempt in range(self.MAX_RETRIES):
            try:
                pdf_content = self._download_receipt(reference, account_suffix)
                return self._parse_receipt(pdf_content)
                
            except requests.HTTPError as e:
                if e.response.status_code == 500 and attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                    continue
                return {"success": False, "error": f"Bank server error: {str(e)}"}
                
            except requests.RequestException as e:
                return {"success": False, "error": f"Network error: {str(e)}"}
                
            except Exception as e:
                return {"success": False, "error": f"Processing error: {str(e)}"}
        
        return {"success": False, "error": "Max retries reached"}
    
    def _validate_inputs(self, reference: str, suffix: str) -> bool:
        """Validate reference and account suffix format"""
        return (reference and suffix and 
                reference.startswith('FT') and 
                re.match(r'^\d{8}$', suffix))
    
    def _download_receipt(self, reference: str, suffix: str) -> bytes:
        """Download PDF with timeout and headers"""
        url = self.CBE_URL.format(reference=reference, suffix=suffix)
        
        response = self.session.get(
            url,
            verify=self.verify_ssl,
            timeout=30,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Accept': 'application/pdf',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        )
        response.raise_for_status()
        
        if 'application/pdf' not in response.headers.get('content-type', ''):
            raise requests.RequestException("Response is not a PDF")
            
        return response.content
    
    def _parse_receipt(self, pdf_content: bytes) -> dict:
        """Parse PDF with multiple date format support"""
        try:
            with pdfplumber.open(BytesIO(pdf_content)) as pdf:
                text = "\n".join(page.extract_text() for page in pdf.pages)
                text = " ".join(text.split())
                
                fields = {
                    'payer': self._extract_field(text, r"Payer\s*:?\s*(.*?)\s+Account"),
                    'receiver': self._extract_field(text, r"Receiver\s*:?\s*(.*?)\s+Account"),
                    'payer_account': self._extract_field(text, r"Account\s*:?\s*([A-Z0-9]?\*{4}\d{4})", 0),
                    'receiver_account': self._extract_field(text, r"Account\s*:?\s*([A-Z0-9]?\*{4}\d{4})", 1),
                    'amount': self._parse_amount(text),
                    'reference': self._extract_field(text, r"Reference No\.?\s*\(VAT Invoice No\)\s*:?\s*([A-Z0-9]+)"),
                    'date': self._parse_date(text)
                }
                
                return {
                    "success": True,
                    **fields,
                    "raw_text": text if not all(fields.values()) else None
                }
                
        except Exception as e:
            raise Exception(f"PDF parsing failed: {str(e)}")
    
    def _parse_amount(self, text: str) -> Optional[float]:
        """Extract and convert amount"""
        amount_text = self._extract_field(text, r"Transferred Amount\s*:?\s*([\d,]+\.\d{2})\s*ETB")
        return float(amount_text.replace(",", "")) if amount_text else None
    
    def _parse_date(self, text: str) -> Optional[str]:
        """Try multiple date formats"""
        date_str = self._extract_field(text, r"Payment Date & Time\s*:?\s*([\d\/,: ]+[APM]{2})")
        if not date_str:
            return None
            
        formats = [
            "%d/%m/%Y, %I:%M:%S %p",  # DD/MM/YYYY
            "%m/%d/%Y, %I:%M:%S %p",  # MM/DD/YYYY
            "%Y/%m/%d, %I:%M:%S %p",  # YYYY/MM/DD
            "%d-%m-%Y, %I:%M:%S %p",  # DD-MM-YYYY
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).isoformat()
            except ValueError:
                continue
                
        return None
    
    def _extract_field(self, text: str, pattern: str, group_index: int = 1) -> Optional[str]:
        """Safe field extraction"""
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(group_index).strip() if match else None
    
    def _title_case(self, text: str) -> str:
        """Format names properly"""
        return text.title() if text else None