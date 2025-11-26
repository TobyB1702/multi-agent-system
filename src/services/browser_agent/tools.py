import asyncio
from pathlib import Path
from langchain.tools import tool
from playwright.async_api import async_playwright
from src.logger.logger import logger
import string
import random

class ToolsContext:
    def __init__(self, screenshot_dir: str = "screenshots"):
        self.memory = {}
        self.screenshot_dir = screenshot_dir
        self.loop = None
        self.session_id = self._generate_session_id()
        self.session_dir = self._create_session_directory()
        Path(screenshot_dir).mkdir(exist_ok=True)

    def _generate_session_id(self) -> str:
        """Generate a random session ID (max 12 characters)."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(8, 12)))
    
    def _create_session_directory(self) -> Path:
        """Create a session-specific directory within screenshot_dir."""
        base_path = Path(self.screenshot_dir)
        base_path.mkdir(exist_ok=True)
        session_path = base_path / self.session_id
        session_path.mkdir(exist_ok=True)
        return session_path

    def set_value(self, key, value):
        self.memory[key] = value

    def get_value(self, key, default=None):
        return self.memory.get(key, default)
    
    def clear_memory(self):
        self.memory = {}
    
    def run_async(self, coro):
        """Run async code in a persistent event loop. Needed otherwise Playwright will fail due to new event loop creation."""
        if self.loop is None or self.loop.is_closed():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        return self.loop.run_until_complete(coro)


class BrowserAgentToolSets:
    def get_tools(self, ctx: ToolsContext):
        """Returns a list of tools in the expected format."""

        @tool
        def launch_browser() -> str:
            """Launches a headless browser session and keeps it open."""
            async def run():
                try:
                    playwright = await async_playwright().start()
                    browser = await playwright.chromium.launch(headless=True)
                    browser_context = await browser.new_context()
                    page = await browser_context.new_page()
                    
                    ctx.set_value("playwright", playwright)
                    ctx.set_value("browser", browser)
                    ctx.set_value("context", browser_context)
                    ctx.set_value("page", page)
                    
                    return "Browser launched successfully."
                except Exception as e:
                    return f"Error launching browser: {str(e)}"
            
            result = ctx.run_async(run())
            logger.info(result)
            return result
    
        @tool
        def go_to_url(url: str) -> str:
            """If the user question requires visiting a website, use this tool to navigate to the specified URL."""
            async def run():
                page = ctx.get_value("page")
                if page is None:
                    return "Browser not launched. Please launch the browser first."
                
                try:
                    await page.goto(url, wait_until="networkidle")
                    ctx.set_value("current_url", url)
                    return f"Navigated to {url}"
                except Exception as e:
                    return f"Error navigating to {url}: {str(e)}"
            
            result = ctx.run_async(run())
            logger.info(result)
            return result

        @tool
        def click_selector(selector: str) -> str:
            """Clicks an element on the page specified by the CSS selector."""
            async def run():
                page = ctx.get_value("page")
                if page is None:
                    return "Browser not launched. Please launch the browser first."
                
                try:
                    await page.click(selector)
                    return f"Clicked element with selector: {selector}"
                except Exception as e:
                    return f"Error clicking element {selector}: {str(e)}"
            
            result = ctx.run_async(run())
            logger.info(result)
            return result
        
        @tool
        def get_page_content() -> str:
            """Retrieves the visible text content of the current page."""
            async def run():
                page = ctx.get_value("page")
                if page is None:
                    return "Browser not launched. Please launch the browser first."
                
                try:
                    visible_text = await page.evaluate("""
                        () => {
                            function isVisible(el) {
                                const style = window.getComputedStyle(el);
                                return style && style.display !== 'none' &&
                                       style.visibility !== 'hidden' &&
                                       style.opacity !== '0' &&
                                       el.offsetHeight > 0 &&
                                       el.offsetWidth > 0;
                            }
                            const walker = document.createTreeWalker(
                                document.body,
                                NodeFilter.SHOW_TEXT
                            );
                            let text = [];
                            let node;
                            while ((node = walker.nextNode())) {
                                if (isVisible(node.parentElement)) {
                                    text.push(node.textContent.trim());
                                }
                            }
                            return text.filter(Boolean).join(" ");
                        }
                    """)
                    ctx.set_value("page_content", visible_text)
                    return visible_text
                except Exception as e:
                    return f"Error retrieving page content: {str(e)}"
            
            result = ctx.run_async(run())
            logger.info("Retrieved page content.")
            return result
        
        @tool
        def take_screenshot(filename: str) -> str:
            """Takes a screenshot of the current page and saves it to the session directory."""
            async def run():
                page = ctx.get_value("page")
                if page is None:
                    return "Browser not launched. Please launch the browser first."
                
                try:
                    # Use filename as-is, no session_id suffix needed since it's in session directory
                    screenshot_path = ctx.session_dir / filename
                    await page.screenshot(path=str(screenshot_path))
                    return f"Screenshot saved to {screenshot_path}"
                except Exception as e:
                    return f"Error taking screenshot: {str(e)}"
            
            result = ctx.run_async(run())
            logger.info(result)
            return result
        
        @tool
        def close_browser() -> str:
            """Closes the headless browser session."""
            async def run():
                browser = ctx.get_value("browser")
                playwright = ctx.get_value("playwright")
                
                if browser is None:
                    return "Browser not launched."
                
                try:
                    await browser.close()
                    await playwright.stop()
                    ctx.clear_memory()
                    return "Browser closed successfully."
                except Exception as e:
                    return f"Error closing browser: {str(e)}"
            
            result = ctx.run_async(run())
            logger.info(result)
            return result
        
        return [launch_browser, go_to_url, click_selector, get_page_content, take_screenshot, close_browser]