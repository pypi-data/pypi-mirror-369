import { RenderData } from "streamlit-component-lib";
import { lighten } from "color2k";
import { hexToRgb } from "./utils";
import { StreamlitAPI } from "./streamlitApi";

let windowRendered = false;
let button: HTMLButtonElement | null = null;
let textElement: HTMLButtonElement | null = null;

// Paint the ship with Streamlit’s colors
function applyTheme(theme: RenderData["theme"]) {
  if (!theme) return;

  const lightenedBg05 = lighten(theme.backgroundColor, 0.025);

  document.documentElement.style.setProperty('--primary-color', theme.primaryColor);
  document.documentElement.style.setProperty('--background-color', theme.backgroundColor);
  document.documentElement.style.setProperty('--text-color', theme.textColor);
  // RGB be the key to mixin’ alpha in the CSS, like blendin’ grog for a translucent glow!
  document.documentElement.style.setProperty('--text-color-rgb', hexToRgb(theme.textColor));
  document.documentElement.style.setProperty('--secondary-background-color', theme.secondaryBackgroundColor);
  document.documentElement.style.setProperty('--lightened-bg05', lightenedBg05);
}

// Rig up the buttons and text
function setupButtons(text: string, show_text: boolean, before_copy_label: string) {
  const span = document.body.appendChild(document.createElement("span"));
  textElement = span.appendChild(document.createElement("button"));
  button = span.appendChild(document.createElement("button"));

  textElement.className = "st-copy-button";
  button.className = "st-copy-button";

  button.textContent = before_copy_label;

  if (show_text) {
    textElement.textContent = text;
    textElement.style.display = "inline";
  } else {
    textElement.style.display = "none";
  }
}

// Fire the copy cannon
function createCopyHandler(text: string, before_copy_label: string, after_copy_label: string) {
  return function () {
    navigator.clipboard.writeText(text.trim());
    if (button) button.textContent = after_copy_label;
    StreamlitAPI.setComponentValue(true);
    setTimeout(() => {
      if (button) button.textContent = before_copy_label;
    }, 1000);
  };
}

// Main render, the captain’s orders
export function onRender(event: CustomEvent<RenderData>): void {
  if (windowRendered) {
    StreamlitAPI.setFrameHeight(40);
    return;
  }

  const { args, theme } = event.detail;
  const { text, before_copy_label, after_copy_label, show_text } = args;

  applyTheme(theme);
  setupButtons(text, show_text, before_copy_label);

  const copyToClipboard = createCopyHandler(text, before_copy_label, after_copy_label);

  if (button) button.addEventListener("click", copyToClipboard);
  if (textElement) textElement.addEventListener("click", copyToClipboard);

  windowRendered = true;
  StreamlitAPI.setFrameHeight(40);
}
