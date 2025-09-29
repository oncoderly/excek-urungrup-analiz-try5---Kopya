$path = "excel_analyzer.py"
$encoding = [System.Text.Encoding]::UTF8
$text = [System.IO.File]::ReadAllText($path, $encoding)

$injectFunction = @"

def ensure_utf8_rendering() -> None:
    st.markdown(
        """
        <script>
        (function() {
            const ensureMeta = () => {
                const existing = document.querySelector('meta[charset]');
                if (existing) {
                    existing.setAttribute('charset', 'utf-8');
                } else {
                    const meta = document.createElement('meta');
                    meta.setAttribute('charset', 'utf-8');
                    document.head.appendChild(meta);
                }
            };

            const decodeText = (value) => {
                try {
                    const decoded = decodeURIComponent(escape(value));
                    return decoded;
                } catch (err) {
                    return value;
                }
            };

            const processNode = (node) => {
                if (!node) return;
                if (node.nodeType === Node.TEXT_NODE) {
                    const updated = decodeText(node.nodeValue);
                    if (updated !== node.nodeValue) {
                        node.nodeValue = updated;
                    }
                } else if (node.nodeType === Node.ELEMENT_NODE) {
                    node.childNodes.forEach(processNode);
                }
            };

            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    mutation.addedNodes.forEach(processNode);
                });
            });

            const run = () => {
                ensureMeta();
                processNode(document.body);
                observer.observe(document.body, { childList: true, subtree: true });
            };

            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', run);
            } else {
                run();
            }

            window.addEventListener('load', () => {
                processNode(document.body);
            });
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )
"""

if ($text -notlike "*def ensure_utf8_rendering()*") {
    $marker = "ensure_aggrid_loaded()\nensure_fpdf_loaded()\n\n"
    if ($text -notlike "*$marker*") { throw 'marker not found for injection' }
    $text = $text -replace [Regex]::Escape($marker), "ensure_aggrid_loaded()\nensure_fpdf_loaded()\n\n$injectFunction$marker"
}

$callMarker = "if _pfpdf_auto_install_succeeded:"  # placeholder to find where to insert call? maybe near start of main? We'll handle separately

[System.IO.File]::WriteAllText($path, $text, $encoding)
