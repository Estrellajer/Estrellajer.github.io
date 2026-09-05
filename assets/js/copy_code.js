// Modern code block window chrome and copy button
function initCodeCopyBlocks() {
  var codeBlocks = document.querySelectorAll("pre");
  codeBlocks.forEach(function (codeBlock) {
    if (
      (codeBlock.querySelector("pre:not(.lineno)") || codeBlock.querySelector("code") || codeBlock.classList.contains("highlight")) &&
      !codeBlock.querySelector("code.language-chartjs") &&
      !codeBlock.querySelector("code.language-diff2html") &&
      !codeBlock.querySelector("code.language-echarts") &&
      !codeBlock.querySelector("code.language-geojson") &&
      !codeBlock.querySelector("code.language-mermaid") &&
      !codeBlock.querySelector("code.language-plotly") &&
      !codeBlock.querySelector("code.language-vega_lite")
    ) {
      // Prevent double wrapping
      if (codeBlock.closest(".code-display-wrapper")) {
        return;
      }

      // Detect language
      var lang = "";
      var codeEl = codeBlock.querySelector("code");
      var searchStr = (codeEl ? codeEl.className : "") + " " + codeBlock.className;
      var langParent = codeBlock.closest("[class*='language-']");
      if (langParent) {
        searchStr += " " + langParent.className;
      }
      var match = searchStr.match(/language-([a-zA-Z0-9_\-]+)/);
      if (match && match[1]) {
        var rawLang = match[1].toLowerCase();
        if (rawLang !== "plaintext" && rawLang !== "text") {
          lang = rawLang;
        }
      }

      // Create window chrome header
      var header = document.createElement("div");
      header.className = "code-header";

      // Mac terminal dots
      var dots = document.createElement("div");
      dots.className = "code-dots";
      dots.innerHTML = '<span class="code-dot dot-red"></span><span class="code-dot dot-yellow"></span><span class="code-dot dot-green"></span>';
      header.appendChild(dots);

      // Language label
      var langBadge = document.createElement("span");
      langBadge.className = "code-lang-badge";
      langBadge.innerText = lang ? lang.toUpperCase() : "CODE";
      header.appendChild(langBadge);

      // Copy button
      var copyButton = document.createElement("button");
      copyButton.className = "code-copy-btn";
      copyButton.type = "button";
      copyButton.setAttribute("aria-label", "Copy code to clipboard");
      copyButton.innerHTML = '<i class="fa-regular fa-clone"></i> <span>Copy</span>';

      copyButton.addEventListener("click", function () {
        var code = "";
        if (codeBlock.querySelector("pre:not(.lineno)")) {
          code = codeBlock.querySelector("pre:not(.lineno)").innerText.trim();
        } else if (codeBlock.querySelector("code")) {
          code = codeBlock.querySelector("code").innerText.trim();
        } else {
          code = codeBlock.innerText.trim();
        }

        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(code).then(function () {
            copyButton.classList.add("copied");
            copyButton.innerHTML = '<i class="fa-solid fa-check"></i> <span>Copied!</span>';
            setTimeout(function () {
              copyButton.classList.remove("copied");
              copyButton.innerHTML = '<i class="fa-regular fa-clone"></i> <span>Copy</span>';
            }, 2200);
          }).catch(function () {
            copyButton.classList.add("copied");
            copyButton.innerHTML = '<i class="fa-solid fa-check"></i> <span>Copied!</span>';
            setTimeout(function () {
              copyButton.classList.remove("copied");
              copyButton.innerHTML = '<i class="fa-regular fa-clone"></i> <span>Copy</span>';
            }, 2200);
          });
        } else {
          copyButton.classList.add("copied");
          copyButton.innerHTML = '<i class="fa-solid fa-check"></i> <span>Copied!</span>';
          setTimeout(function () {
            copyButton.classList.remove("copied");
            copyButton.innerHTML = '<i class="fa-regular fa-clone"></i> <span>Copy</span>';
          }, 2200);
        }
      });

      header.appendChild(copyButton);

      // Wrapper
      var wrapper = document.createElement("div");
      wrapper.className = "code-display-wrapper";

      var targetNode = codeBlock;
      var rougeParent = codeBlock.closest(".highlighter-rouge");
      if (rougeParent && !rougeParent.closest(".code-display-wrapper")) {
        targetNode = rougeParent;
      }

      var parent = targetNode.parentElement;
      parent.insertBefore(wrapper, targetNode);
      wrapper.appendChild(header);
      wrapper.appendChild(targetNode);
    }
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initCodeCopyBlocks);
} else {
  initCodeCopyBlocks();
}
