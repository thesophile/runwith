var editor = CodeMirror.fromTextArea(document.getElementById('code'), {
    mode: 'python',
    lineNumbers: true,
    tabSize: 4,
    // value: 'from manim import*',
    theme: 'monokai',
    extraKeys: {
        "Ctrl-Space": "autocomplete",
        "Ctrl-Shift-F": "replace",
        "Ctrl-/": "toggleComment"
    }
});


// shortcuts 
// mod = Ctrl on Win/Linux, Cmd on Mac
const shortcuts = [
    {
        key: "s",
        mod: true,
        shift: false,
        alt: false,
        action: () => document.getElementById("save-btn").click()
    },
    {
        key: "n",
        mod: true,
        shift: false,
        alt: true,
        action: () => document.getElementById("new-btn").click()
    },
    {
        key: "Enter",
        mod: true,
        shift: false,
        alt: false,
        action: () => document.getElementById("run-btn").click()
    }
];

// Main listener
document.addEventListener("keydown", (e) => {
    for (const s of shortcuts) {
        const keyMatch = e.key.toLowerCase() === s.key.toLowerCase();
        const modMatch = s.mod ? (e.ctrlKey || e.metaKey) : (!e.ctrlKey && !e.metaKey);
        const shiftMatch = s.shift ? e.shiftKey : !e.shiftKey;
        const altMatch = s.alt ? e.altKey : !e.altKey;

        if (keyMatch && modMatch && shiftMatch && altMatch) {
            e.preventDefault();   // prevent browser default only for this shortcut
            s.action();
            break;                // stop after first match
        }
    }
});


//theme toggle

const themeToggle = document.querySelector('.theme-toggle input');

themeToggle.addEventListener('change', () => {
    if (themeToggle.checked) {
        editor.setOption('theme', 'eclipse');
    } else {
        editor.setOption('theme', 'monokai');
    }
});