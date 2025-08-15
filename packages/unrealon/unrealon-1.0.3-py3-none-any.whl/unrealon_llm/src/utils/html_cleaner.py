"""
Smart HTML Cleaner

Intelligent HTML cleaning that removes noise but preserves useful data.
Optimizes HTML for LLM token efficiency while keeping valuable content.
"""

import json
import re
from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup, Comment

from unrealon_llm.src.exceptions import ValidationError


class SmartHTMLCleaner:
    """
    Intelligent HTML cleaner that optimizes for LLM analysis
    
    Features:
    - Removes noise (scripts, styles, comments)
    - Preserves useful JavaScript data (JSON objects, SSR data)
    - Cleans whitespace and formatting
    - Maintains semantic structure
    - Extracts and preserves Next.js/Nuxt.js SSR data
    """
    
    def __init__(self):
        """Initialize the HTML cleaner"""
        # Tags to completely remove
        self.noise_tags = {
            'script', 'style', 'meta', 'link', 'base', 'title',
            'head', 'noscript', 'iframe', 'embed', 'object',
            'svg', 'canvas', 'audio', 'video', 'source',
            'track', 'area', 'map', 'param', 'form', 'input',
            'button', 'select', 'textarea', 'fieldset', 'legend'
        }
        
        # URL patterns to remove or shorten (for tracking/analytics)
        self.tracking_url_patterns = [
            r'https://aax-[^\s"]{200,}',  # Amazon tracking URLs over 200 chars
            r'https://[^\s"]*tracking[^\s"]{100,}',  # General tracking URLs
            r'https://[^\s"]*analytics[^\s"]{100,}',  # Analytics URLs
            r'https://[^\s"]*gtm[^\s"]{100,}',  # Google Tag Manager URLs
        ]
        
        # Base64 patterns to remove or replace
        self.base64_patterns = [
            r'data:image/[^;]+;base64,[A-Za-z0-9+/=]{50,}',  # Base64 images over 50 chars
            r'data:application/[^;]+;base64,[A-Za-z0-9+/=]{100,}',  # Base64 applications
            r'data:text/[^;]+;base64,[A-Za-z0-9+/=]{100,}',  # Base64 text
        ]
        
        # Universal noise selectors to remove (for any site)
        self.universal_noise_selectors = [
            '[id*="nav"]', '[class*="nav"]',           # Navigation
            '[id*="menu"]', '[class*="menu"]',         # Menus
            '[id*="sidebar"]', '[class*="sidebar"]',   # Sidebars
            '[id*="footer"]', '[class*="footer"]',     # Footers
            '[id*="header"]', '[class*="header"]',     # Headers
            '[class*="ads"]', '[class*="advertisement"]', # Ads
            '[class*="sponsored"]', '[class*="promo"]', # Sponsored content
            '[class*="popup"]', '[class*="modal"]',    # Popups/modals
            '[class*="overlay"]', '[class*="tooltip"]', # Overlays
            '[class*="cookie"]', '[class*="gdpr"]',    # Cookie notices
            '[class*="newsletter"]', '[class*="subscription"]', # Email signup
            '[class*="social"]', '[class*="share"]',   # Social media
            '[class*="comment"]', '[class*="discussion"]', # Comments (unless main content)
            '[class*="tracking"]', '[class*="analytics"]', # Tracking
        ]
        
        # Attributes to remove (keep only semantic ones)
        self.noise_attributes = {
            'style', 'onclick', 'onload', 'onchange', 'onmouseover',
            'onmouseout', 'onfocus', 'onblur', 'onsubmit', 'onreset',
            'onerror', 'onabort', 'oncanplay', 'oncanplaythrough',
            'ondurationchange', 'onemptied', 'onended', 'onloadeddata',
            'onloadedmetadata', 'onloadstart', 'onpause', 'onplay',
            'onplaying', 'onprogress', 'onratechange', 'onseeked',
            'onseeking', 'onstalled', 'onsuspend', 'ontimeupdate',
            'onvolumechange', 'onwaiting', 'onkeydown', 'onkeypress',
            'onkeyup', 'onmousedown', 'onmousemove', 'onmouseup',
            'onwheel', 'ondrag', 'ondragend', 'ondragenter',
            'ondragleave', 'ondragover', 'ondragstart', 'ondrop',
            'onscroll', 'onresize', 'onstorage', 'onhashchange',
            'onpopstate', 'onbeforeprint', 'onafterprint',
            'onbeforeunload', 'onunload', 'onmessage', 'oninput',
            'oninvalid', 'onsearch', 'autocomplete', 'autofocus',
            'checked', 'defer', 'disabled', 'hidden', 'loop',
            'multiple', 'muted', 'open', 'readonly', 'required',
            'reversed', 'selected', 'autoplay', 'controls',
            'crossorigin', 'download', 'hreflang', 'ismap',
            'itemid', 'itemprop', 'itemref', 'itemscope',
            'itemtype', 'kind', 'media', 'rel', 'sandbox',
            'scope', 'sizes', 'span', 'spellcheck', 'srcdoc',
            'srclang', 'srcset', 'step', 'tabindex', 'target',
            'translate', 'usemap', 'wrap', 'accept', 'acceptcharset',
            'accesskey', 'action', 'allowfullscreen', 'alt',
            'async', 'autocapitalize', 'capture', 'charset',
            'cols', 'colspan', 'content', 'contenteditable',
            'contextmenu', 'coords', 'datetime', 'decoding',
            'default', 'dir', 'dirname', 'download', 'draggable',
            'enctype', 'enterkeyhint', 'for', 'form', 'formaction',
            'formenctype', 'formmethod', 'formnovalidate',
            'formtarget', 'headers', 'height', 'high', 'href',
            'hreflang', 'httpequiv', 'icon', 'importance', 'inputmode',
            'integrity', 'intrinsicsize', 'keytype', 'label',
            'lang', 'list', 'loading', 'low', 'manifest',
            'max', 'maxlength', 'method', 'min', 'minlength',
            'name', 'novalidate', 'optimum', 'pattern',
            'ping', 'placeholder', 'poster', 'preload',
            'radiogroup', 'referrerpolicy', 'rows', 'rowspan',
            'shape', 'size', 'slot', 'src', 'start',
            'title', 'type', 'value', 'width'
        }
        
        # Keep these semantic attributes
        self.keep_attributes = {
            'id', 'class', 'data-testid', 'data-test', 'data-cy',
            'aria-label', 'aria-labelledby', 'aria-describedby',
            'role', 'alt', 'title', 'href', 'src', 'action',
            'name', 'value', 'placeholder', 'type'
        }
        
        # Patterns to detect valuable JavaScript data
        self.useful_js_patterns = [
            # Next.js/Nuxt.js SSR data
            r'__NEXT_DATA__\s*=\s*(\{.+?\});?',
            r'__NUXT__\s*=\s*(\{.+?\});?',
            r'window\.__INITIAL_STATE__\s*=\s*(\{.+?\});?',
            
            # React/Vue hydration data  
            r'window\.__REACT_QUERY_STATE__\s*=\s*(\{.+?\});?',
            r'window\.__VUE_SSR_CONTEXT__\s*=\s*(\{.+?\});?',
            
            # E-commerce data
            r'window\.productData\s*=\s*(\{.+?\});?',
            r'window\.cartData\s*=\s*(\{.+?\});?',
            r'dataLayer\s*=\s*(\[.+?\]);?',
            
            # Analytics and tracking (structured data)
            r'gtag\s*\(\s*[\'"]config[\'"],\s*[\'"][^\'\"]+[\'"],\s*(\{.+?\})\s*\);?',
            
            # JSON-LD structured data (often in script tags)
            r'"@context"\s*:\s*"https?://schema\.org"[^}]*\}',
            
            # Generic JSON objects (be more selective)
            r'(?:window\.|var\s+|let\s+|const\s+)\w+\s*=\s*(\{.+?\});?',
        ]
        
        # Compiled regex patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.DOTALL | re.IGNORECASE) 
                                 for pattern in self.useful_js_patterns]
    
    def clean_html(
        self, 
        html_content: str, 
        preserve_js_data: bool = True,
        aggressive_cleaning: bool = False
    ) -> Tuple[str, Dict[str, any]]:
        """
        Clean HTML content while preserving valuable data
        
        Args:
            html_content: Raw HTML content
            preserve_js_data: Whether to extract and preserve JS data
            aggressive_cleaning: Whether to apply more aggressive cleaning
            
        Returns:
            Tuple of (cleaned_html, extracted_data)
        """
        if not html_content or not html_content.strip():
            return "", {}
        
        # Parse HTML
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            raise ValidationError(f"Failed to parse HTML: {e}")
        
        extracted_data = {}
        
        # Extract valuable JavaScript data before removing scripts
        if preserve_js_data:
            extracted_data = self._extract_js_data(soup)
        
        # Remove universal noise elements for aggressive cleaning
        if aggressive_cleaning:
            self._remove_universal_noise(soup)
            self._truncate_long_urls(soup)  # Do this before tracking URL cleaning
            self._clean_tracking_urls(soup)
            self._clean_base64_data(soup)
            self._remove_long_attributes(soup)
            self._remove_html_comments(soup)
            self._clean_whitespace(soup)
        
        # Remove noise elements
        self._remove_noise_elements(soup)
        
        # Clean attributes
        self._clean_attributes(soup, aggressive_cleaning)
        
        # Remove comments
        self._remove_comments(soup)
        
        # Clean text and whitespace
        cleaned_html = self._clean_text_and_whitespace(soup)
        
        # Final cleanup
        cleaned_html = self._final_cleanup(cleaned_html)
        
        return cleaned_html, extracted_data
    
    def _extract_js_data(self, soup: BeautifulSoup) -> Dict[str, any]:
        """Extract valuable data from JavaScript"""
        extracted_data = {
            'ssr_data': {},
            'structured_data': [],
            'analytics_data': {},
            'product_data': {},
            'raw_extracts': []
        }
        
        # Find all script tags
        script_tags = soup.find_all('script')
        
        for script in script_tags:
            if not script.string:
                continue
                
            script_content = script.string.strip()
            
            # Skip empty or very short scripts
            if len(script_content) < 10:
                continue
            
            # Check for JSON-LD structured data
            if script.get('type') == 'application/ld+json':
                try:
                    json_data = json.loads(script_content)
                    extracted_data['structured_data'].append(json_data)
                    continue
                except json.JSONDecodeError:
                    pass
            
            # Extract data using patterns
            self._extract_with_patterns(script_content, extracted_data)
        
        # Remove empty categories
        extracted_data = {k: v for k, v in extracted_data.items() if v}
        
        return extracted_data
    
    def _extract_with_patterns(self, script_content: str, extracted_data: Dict):
        """Extract data using compiled regex patterns and heuristics"""
        
        # First try specific named patterns
        self._extract_named_patterns(script_content, extracted_data)
        
        # Then try generic JSON extraction as fallback
        self._extract_generic_json(script_content, extracted_data)
    
    def _extract_named_patterns(self, script_content: str, extracted_data: Dict):
        """Extract data using specific named patterns"""
        
        # Next.js SSR data
        nextjs_patterns = [
            r'__NEXT_DATA__\s*=\s*({.+?});',
            r'window\.__NEXT_DATA__\s*=\s*({.+?});'
        ]
        
        for pattern in nextjs_patterns:
            matches = re.finditer(pattern, script_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                self._try_parse_json(match.group(1), extracted_data, 'ssr_data')
        
        # React Query state
        react_patterns = [
            r'window\.__REACT_QUERY_STATE__\s*=\s*({.+?});'
        ]
        
        for pattern in react_patterns:
            matches = re.finditer(pattern, script_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                self._try_parse_json(match.group(1), extracted_data, 'ssr_data')
        
        # Product data
        product_patterns = [
            r'window\.productData\s*=\s*({.+?});',
            r'dataLayer\s*=\s*(\[.+?\]);'
        ]
        
        for pattern in product_patterns:
            matches = re.finditer(pattern, script_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                self._try_parse_json(match.group(1), extracted_data, 'product_data')
    
    def _extract_generic_json(self, script_content: str, extracted_data: Dict):
        """Extract generic JSON objects as fallback"""
        
        # Look for variable assignments with objects
        generic_patterns = [
            r'(?:window\.|var\s+|let\s+|const\s+)(\w+)\s*=\s*({[^;]+});',
            r'(\w+)\s*=\s*({[^;]+});'
        ]
        
        for pattern in generic_patterns:
            matches = re.finditer(pattern, script_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                var_name = match.group(1)
                json_content = match.group(2)
                
                # Only process if it looks like substantial data
                if len(json_content) > 20:
                    self._try_parse_json(json_content, extracted_data, 'raw_extracts', var_name)
    
    def _try_parse_json(self, json_str: str, extracted_data: Dict, category: str, var_name: str = None):
        """Try to parse JSON string and categorize it"""
        try:
            json_data = json.loads(json_str)
            
            if category == 'ssr_data':
                if 'ssr_data' not in extracted_data:
                    extracted_data['ssr_data'] = {}
                if isinstance(json_data, dict):
                    extracted_data['ssr_data'].update(json_data)
                else:
                    extracted_data['ssr_data'][var_name or 'data'] = json_data
                    
            elif category == 'product_data':
                if 'product_data' not in extracted_data:
                    extracted_data['product_data'] = {}
                if isinstance(json_data, dict):
                    extracted_data['product_data'].update(json_data)
                else:
                    extracted_data['product_data'][var_name or 'data'] = json_data
                    
            else:  # raw_extracts - filter useful ones only
                # Only store raw extracts if they look like complete objects
                if isinstance(json_data, dict) and len(json_data) > 3:
                    if 'raw_extracts' not in extracted_data:
                        extracted_data['raw_extracts'] = []
                    extracted_data['raw_extracts'].append(json_data)
                    
        except json.JSONDecodeError:
            # Skip invalid JSON - it's noise
            pass
    
    def _remove_noise_elements(self, soup: BeautifulSoup):
        """Remove noise HTML elements"""
        # Remove noise tags
        for tag_name in self.noise_tags:
            for tag in soup.find_all(tag_name):
                tag.decompose()
        
        # Remove empty divs and spans
        for tag in soup.find_all(['div', 'span']):
            if not tag.get_text(strip=True) and not tag.find_all():
                tag.decompose()
    
    def _clean_attributes(self, soup: BeautifulSoup, aggressive: bool = False):
        """Clean HTML attributes"""
        for tag in soup.find_all(True):  # Find all tags
            if hasattr(tag, 'attrs'):
                # Determine which attributes to keep
                if aggressive:
                    # Keep only essential semantic attributes
                    keep_attrs = self.keep_attributes & {'id', 'class', 'href', 'src', 'alt'}
                else:
                    keep_attrs = self.keep_attributes
                
                # Remove unwanted attributes
                attrs_to_remove = set(tag.attrs.keys()) - keep_attrs
                for attr in attrs_to_remove:
                    del tag.attrs[attr]
                
                # Clean class names (remove utility classes if aggressive)
                if aggressive and 'class' in tag.attrs:
                    classes = tag.attrs['class']
                    if isinstance(classes, list):
                        # Remove utility classes (Tailwind, Bootstrap, etc.)
                        semantic_classes = [
                            cls for cls in classes 
                            if not self._is_utility_class(cls)
                        ]
                        if semantic_classes:
                            tag.attrs['class'] = semantic_classes
                        else:
                            del tag.attrs['class']
    
    def _remove_universal_noise(self, soup: BeautifulSoup):
        """Remove universal noise elements from any website"""
        for selector in self.universal_noise_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    # Keep only main product content areas
                    if not self._is_main_content_element(element):
                        element.decompose()
            except Exception:
                # Skip invalid selectors
                continue
                        
    def _clean_tracking_urls(self, soup: BeautifulSoup):
        """Remove or shorten tracking URLs that bloat HTML size"""
        import re
        
        # Clean href attributes in links
        for tag in soup.find_all(['a'], href=True):
            href = tag.get('href', '')
            if href and not href.endswith('...truncated'):  # Skip already truncated URLs
                for pattern in self.tracking_url_patterns:
                    if re.match(pattern, href):
                        # Replace with placeholder for tracking URLs
                        tag['href'] = '#tracking-url-removed'
                        break
                        
        # Clean src attributes in images
        for tag in soup.find_all(['img'], src=True):
            src = tag.get('src', '')
            if src:
                for pattern in self.tracking_url_patterns:
                    if re.match(pattern, src):
                        # Replace with minimal SVG placeholder
                        tag['src'] = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/%3E'
                        break
                        
    def _clean_base64_data(self, soup: BeautifulSoup):
        """Remove or replace large base64 encoded data to reduce HTML size"""
        import re
        
        # Clean base64 data in img src attributes
        for tag in soup.find_all(['img'], src=True):
            src = tag.get('src', '')
            if src:
                for pattern in self.base64_patterns:
                    if re.search(pattern, src):
                        # Extract image type if possible
                        if src.startswith('data:image/'):
                            # Replace with minimal SVG placeholder
                            tag['src'] = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/%3E'
                        else:
                            # Remove the src entirely for non-images
                            del tag['src']
                        break
                        
        # Clean base64 data in style attributes and CSS
        for tag in soup.find_all(style=True):
            style = tag.get('style', '')
            if style:
                for pattern in self.base64_patterns:
                    if re.search(pattern, style):
                        # Remove the entire style attribute if it contains large base64
                        del tag['style']
                        break
                        
        # Clean base64 data in href attributes (for downloads, etc.)
        for tag in soup.find_all(['a'], href=True):
            href = tag.get('href', '')
            if href:
                for pattern in self.base64_patterns:
                    if re.match(pattern, href):
                        # Replace with placeholder
                        tag['href'] = '#base64-data-removed'
                        break
                        
        # Clean base64 data from any attribute (catch-all)
        for tag in soup.find_all():
            attrs_to_clean = []
            for attr, value in tag.attrs.items():
                if isinstance(value, str):
                    for pattern in self.base64_patterns:
                        if re.search(pattern, value):
                            attrs_to_clean.append(attr)
                            break
                            
            # Clean or remove attributes with base64 data
            for attr in attrs_to_clean:
                if attr in ['src', 'href']:
                    # Replace with placeholder for important attributes
                    if attr == 'src':
                        tag[attr] = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/%3E'
                    else:
                        tag[attr] = '#base64-data-removed'
                else:
                    # Remove entirely for other attributes
                    del tag.attrs[attr]
                        
    def _truncate_long_urls(self, soup: BeautifulSoup, max_url_length: int = 500):
        """Truncate any URL longer than max_url_length characters"""
        
        # Process all elements with href attributes (links)
        for tag in soup.find_all(['a'], href=True):
            href = tag.get('href', '')
            if isinstance(href, str) and len(href) > max_url_length:
                # Keep the beginning of the URL and add indicator
                truncated_url = href[:max_url_length] + '...truncated'
                tag['href'] = truncated_url
                
        # Process all elements with src attributes (images, iframes, etc.)
        for tag in soup.find_all(['img', 'iframe', 'embed', 'object'], src=True):
            src = tag.get('src', '')
            if isinstance(src, str) and len(src) > max_url_length:
                # For images, if it's not base64, truncate it
                if not src.startswith('data:'):
                    truncated_url = src[:max_url_length] + '...truncated'
                    tag['src'] = truncated_url
                # Base64 data is handled by _clean_base64_data method
                
        # Process any other URL-like attributes
        url_attributes = ['action', 'formaction', 'poster', 'cite', 'data', 'manifest']
        for tag in soup.find_all():
            for attr in url_attributes:
                if tag.has_attr(attr):
                    value = tag.get(attr, '')
                    if isinstance(value, str) and len(value) > max_url_length:
                        # Check if it looks like a URL (contains :// or starts with / or http)
                        if ('://' in value or 
                            value.startswith('/') or 
                            value.startswith('http') or 
                            value.startswith('//')):
                            truncated_url = value[:max_url_length] + '...truncated'
                            tag[attr] = truncated_url
                            
    def _remove_long_attributes(self, soup: BeautifulSoup):
        """Remove attributes with extremely long values that are likely tracking data"""
        for tag in soup.find_all():
            # Check all attributes for excessive length
            attrs_to_remove = []
            for attr, value in tag.attrs.items():
                if isinstance(value, str):
                    # Remove attributes longer than 800 chars (likely tracking data)
                    # Increased from 500 since URLs are now handled separately
                    if len(value) > 800:
                        attrs_to_remove.append(attr)
                    # Remove specific tracking attributes regardless of length
                    elif any(tracking in attr.lower() for tracking in 
                           ['tracking', 'analytics', 'gtm', 'pixel', 'impression', 'asin']):
                        attrs_to_remove.append(attr)
                elif isinstance(value, list):
                    # Check if list contains very long strings
                    if any(isinstance(v, str) and len(v) > 500 for v in value):
                        attrs_to_remove.append(attr)
                        
            # Remove the problematic attributes
            for attr in attrs_to_remove:
                del tag.attrs[attr]
                
    def get_cleaning_stats(self, original_size: int, cleaned_size: int) -> Dict[str, any]:
        """Get statistics about the cleaning process"""
        reduction_bytes = original_size - cleaned_size
        reduction_percent = (reduction_bytes / original_size * 100) if original_size > 0 else 0
        
        return {
            'original_size': original_size,
            'cleaned_size': cleaned_size,
            'reduction_bytes': reduction_bytes,
            'reduction_percent': round(reduction_percent, 2),
            'compression_ratio': round(original_size / cleaned_size, 2) if cleaned_size > 0 else 0
        }
        
    def _remove_html_comments(self, soup: BeautifulSoup):
        """Remove all HTML comments to reduce size"""
        # Remove all HTML comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
            
    def _clean_whitespace(self, soup: BeautifulSoup):
        """Clean excessive whitespace in text content"""
        import re
        
        # Process all text nodes
        for element in soup.find_all(text=True):
            if element.parent.name not in ['script', 'style']:  # Skip scripts and styles
                # Replace multiple spaces with single space
                cleaned_text = re.sub(r' {3,}', '  ', str(element))
                # Replace multiple newlines with maximum 2
                cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
                # Replace multiple tabs with single space
                cleaned_text = re.sub(r'\t+', ' ', cleaned_text)
                # Clean mixed whitespace
                cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)
                element.replace_with(cleaned_text)

    def _advanced_whitespace_cleanup(self, html_content: str) -> str:
        """Advanced whitespace cleanup for aggressive cleaning"""
        import re
        
        # Remove excessive spaces (more than 2)
        html_content = re.sub(r' {3,}', '  ', html_content)
        
        # Remove excessive newlines (more than 2)
        html_content = re.sub(r'\n{3,}', '\n\n', html_content)
        
        # Remove excessive tabs
        html_content = re.sub(r'\t{2,}', '\t', html_content)
        
        # Clean mixed whitespace patterns
        html_content = re.sub(r'[ \t]{3,}', '  ', html_content)
        
        # Remove whitespace at line endings
        html_content = re.sub(r'[ \t]+\n', '\n', html_content)
        
        # Remove whitespace at line beginnings (except single indent)
        html_content = re.sub(r'\n[ \t]{2,}', '\n ', html_content)
        
        # Clean space between tags
        html_content = re.sub(r'>\s{2,}<', '> <', html_content)
        
        # Final cleanup
        html_content = html_content.strip()
        
        return html_content
    
    def _is_main_content_element(self, element) -> bool:
        """Check if element contains main product content"""
        # Keep elements that likely contain product info
        product_indicators = [
            'product', 'detail', 'title', 'price', 'description',
            'spec', 'review', 'rating', 'availability', 'image'
        ]
        
        element_text = str(element).lower()
        for indicator in product_indicators:
            if indicator in element_text:
                return True
        return False

    def _is_utility_class(self, class_name: str) -> bool:
        """Check if a class name is a utility class"""
        utility_patterns = [
            r'^(m|p)[trblxy]?-\d+$',        # Margin/padding utilities
            r'^(m|p)[xy]-auto$',            # Margin auto utilities  
            r'^(w|h)-\d+$',                 # Width/height utilities
            r'^text-(xs|sm|lg|xl|\d+xl)$',  # Text size utilities
            r'^bg-\w+(-\d+)?$',             # Background utilities
            r'^text-\w+(-\d+)?$',           # Text color utilities
            r'^border(-\w+)?(-\d+)?$',      # Border utilities
            r'^flex(-\w+)?$',               # Flex utilities
            r'^grid(-\w+)?$',               # Grid utilities
            r'^hidden$',                    # Visibility utilities
            r'^sr-only$',                   # Screen reader utilities
            r'^(sm|md|lg|xl|2xl):.*$',      # Responsive prefixes
            r'^\w+-\d+$',                   # Generic number-based utilities
            r'^mx-auto$',                   # Margin x auto
            r'^my-auto$',                   # Margin y auto
        ]
        
        return any(re.match(pattern, class_name) for pattern in utility_patterns)
    
    def _truncate_long_text_content(self, soup: BeautifulSoup, max_text_length: int = 300):
        """Truncate text content longer than max_text_length characters"""
        # Process all text nodes in the soup
        for element in soup.find_all(text=True):
            # Skip script and style tags
            if element.parent.name in ['script', 'style']:
                continue
                
            text_content = str(element).strip()
            
            # Only process non-empty text that's longer than the limit
            if text_content and len(text_content) > max_text_length:
                # Truncate and add ellipsis
                truncated_text = text_content[:max_text_length] + '...'
                element.replace_with(truncated_text)
    
    def _remove_comments(self, soup: BeautifulSoup):
        """Remove HTML comments"""
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
    
    def _clean_text_and_whitespace(self, soup: BeautifulSoup) -> str:
        """Clean text content and normalize whitespace"""
        # Truncate long text content before converting to string
        self._truncate_long_text_content(soup)
        
        # Get the HTML string
        html_str = str(soup)
        
        # Normalize whitespace
        html_str = re.sub(r'\s+', ' ', html_str)  # Multiple spaces to single
        html_str = re.sub(r'\n\s*\n', '\n', html_str)  # Multiple newlines to single
        html_str = re.sub(r'>\s+<', '><', html_str)  # Remove spaces between tags
        
        return html_str
    
    def _final_cleanup(self, html_content: str) -> str:
        """Final cleanup and optimization"""
        # Remove empty attributes
        html_content = re.sub(r'\s+\w+=""', '', html_content)
        
        # Remove extra spaces in attributes
        html_content = re.sub(r'(\w+)=\s*"([^"]*)"', r'\1="\2"', html_content)
        
        # Normalize quotes
        html_content = re.sub(r"(\w+)='([^']*)'", r'\1="\2"', html_content)
        
        # Remove trailing spaces before closing tags
        html_content = re.sub(r'\s+(/?>)', r'\1', html_content)
        
        # Enhanced whitespace cleanup
        html_content = self._advanced_whitespace_cleanup(html_content)
        
        return html_content.strip()
    
    def get_cleaning_stats(self, original_html: str, cleaned_html: str) -> Dict[str, any]:
        """Get statistics about the cleaning process"""
        original_size = len(original_html)
        cleaned_size = len(cleaned_html)
        
        # Estimate token reduction (rough approximation)
        original_tokens = original_size // 4  # Rough estimate: 4 chars per token
        cleaned_tokens = cleaned_size // 4
        
        return {
            "original_size_bytes": original_size,
            "cleaned_size_bytes": cleaned_size,
            "size_reduction_bytes": original_size - cleaned_size,
            "size_reduction_percent": ((original_size - cleaned_size) / original_size * 100) if original_size > 0 else 0,
            "estimated_original_tokens": original_tokens,
            "estimated_cleaned_tokens": cleaned_tokens,
            "estimated_token_savings": original_tokens - cleaned_tokens,
            "estimated_token_savings_percent": ((original_tokens - cleaned_tokens) / original_tokens * 100) if original_tokens > 0 else 0
        }


# Convenience functions
def clean_html_for_llm(
    html_content: str,
    preserve_js_data: bool = True,
    aggressive_cleaning: bool = False
) -> Tuple[str, Dict[str, any]]:
    """
    Quick function to clean HTML for LLM analysis
    
    Args:
        html_content: Raw HTML content
        preserve_js_data: Whether to extract and preserve JS data
        aggressive_cleaning: Whether to apply aggressive cleaning
        
    Returns:
        Tuple of (cleaned_html, extracted_data)
    """
    cleaner = SmartHTMLCleaner()
    return cleaner.clean_html(html_content, preserve_js_data, aggressive_cleaning)


def extract_js_data_only(html_content: str) -> Dict[str, any]:
    """
    Extract only JavaScript data without cleaning HTML
    
    Args:
        html_content: Raw HTML content
        
    Returns:
        Extracted JavaScript data
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        cleaner = SmartHTMLCleaner()
        return cleaner._extract_js_data(soup)
    except Exception:
        return {}



