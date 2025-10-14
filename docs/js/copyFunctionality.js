// Copy functionality for installation box and code blocks

export function initCopyFunctionality() {
    // Copy functionality for installation box
    const installCopyBtn = document.querySelector('.install-copy-btn');
    
    if (installCopyBtn) {
        installCopyBtn.addEventListener('click', () => {
            const command = 'pip install autotrend';
            
            navigator.clipboard.writeText(command).then(() => {
                // Change icon to checkmark
                installCopyBtn.innerHTML = '<i class="fas fa-check"></i>';
                installCopyBtn.classList.add('copied');
                
                // Reset after 2 seconds
                setTimeout(() => {
                    installCopyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                    installCopyBtn.classList.remove('copied');
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy:', err);
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = command;
                document.body.appendChild(textArea);
                textArea.select();
                try {
                    document.execCommand('copy');
                    installCopyBtn.innerHTML = '<i class="fas fa-check"></i>';
                    installCopyBtn.classList.add('copied');
                    setTimeout(() => {
                        installCopyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                        installCopyBtn.classList.remove('copied');
                    }, 2000);
                } catch (err) {
                    console.error('Fallback copy failed:', err);
                }
                document.body.removeChild(textArea);
            });
        });
    }

    // Copy code block functionality
    document.querySelectorAll('pre code').forEach(block => {
        const pre = block.parentElement;
        
        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.innerHTML = '<i class="fas fa-copy"></i>';
        copyButton.title = 'Copy to clipboard';
        
        // Add button to pre element
        pre.style.position = 'relative';
        pre.appendChild(copyButton);
        
        // Copy functionality
        copyButton.addEventListener('click', () => {
            const code = block.textContent;
            navigator.clipboard.writeText(code).then(() => {
                copyButton.innerHTML = '<i class="fas fa-check"></i>';
                copyButton.style.color = '#10b981';
                
                setTimeout(() => {
                    copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                    copyButton.style.color = '';
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy:', err);
            });
        });
    });

    // Add CSS for copy button dynamically
    const style = document.createElement('style');
    style.textContent = `
        pre {
            position: relative;
        }
        
        .copy-button {
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #e2e8f0;
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.3s;
            opacity: 0;
        }
        
        pre:hover .copy-button {
            opacity: 1;
        }
        
        .copy-button:hover {
            background-color: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.3);
        }
        
        .copy-button:active {
            transform: scale(0.95);
        }
    `;
    document.head.appendChild(style);
}