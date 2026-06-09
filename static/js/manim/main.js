

const modal = document.getElementById("save-modal");
const closeButtons = modal.querySelectorAll(".close");

// Get the button that opens the modal
var savenewBtn = document.getElementById("new-btn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];
var openDropdown = document.getElementById("saved-codes");
var saveBtn = document.getElementById("save-btn");
var SaveCurrentForm = document.getElementById("save-current-form");


const openButton = document.getElementById('open-button');
const openList = document.getElementById('open-list');
// const noOptionsMessage = document.getElementById('no-options-message');

const examplesButton = document.getElementById('examples-button');
const examplesList = document.getElementById('examples-list');

savenewBtn.onclick = function () {
    if (isAuthenticated) {
        document.getElementById("save-modal").classList.add("show");
    }
    else {
        alert("Dude, You have to Log in to save as new");
    }
}

span.onclick = function () {
    document.getElementById("save-modal").classList.remove("show");
}

window.onclick = function (event) {
    if (event.target == modal) {
        document.getElementById("save-modal").classList.remove("show");
    }
}

closeButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        modal.classList.remove("show");
    });
});

document.getElementById("save-new-form").onsubmit = function () {
    var name = document.getElementById("name").value.trim();
    if (name === "") {
        alert("Please enter a name for the code.");
        return false; // Prevent form submission
    }
    else {
        console.log(`New code name: ${name}`);
        setCodeName(name);
        editor.setValue('');
    }
}

document.getElementById('save-new-form').addEventListener('submit', function (event) {
    var visible_code = document.getElementById('code').value;
    // console.log(`visible_code: ${visible_code}`);
    var hidden_code = document.getElementById('hidden_code_new');
    hidden_code.value = visible_code;
});




// Toggle dropdown list visibility
openButton.onclick = function (event) {
    if (!isAuthenticated) {
        event.preventDefault();
        alert('You will have to Log in to do that');
        return;
    }

    const options = openList.querySelectorAll('.dropdown-item');
    console.log(options.length);
    if (options.length === 0) {
        alert("You have no saved projects. Create a new project first.");
        return;
    } else {
        openList.style.display = openList.style.display === "none" ? "block" : "none";
    }
};



// open projects
openList.addEventListener('click', function (event) {
    const editBtn = event.target.closest('.edit-code-btn');
    if (editBtn) {
        event.stopPropagation();
        event.preventDefault();
        const codeId = editBtn.dataset.id;
        const currentName = editBtn.dataset.name;
        const newName = prompt('Rename project:', currentName);
        if (!newName || newName.trim() === currentName) return;

        fetch(`rename_code/${codeId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: JSON.stringify({ name: newName.trim() }),
        }).then(res => {
            if (res.ok) {
                editBtn.dataset.name = newName.trim();
                editBtn.closest('.dropdown-item').querySelector('.dropdown-item-name').textContent = newName.trim();
            } else {
                alert('Failed to rename.');
            }
        });
        return;
    }

    const deleteBtn = event.target.closest('.delete-code-btn');
    if (deleteBtn) {
        event.stopPropagation();
        event.preventDefault();
        const codeId = deleteBtn.dataset.id;
        if (!confirm('Delete this project?')) return;

        fetch(`delete_code/${codeId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        }).then(res => {
            if (res.ok) {
                deleteBtn.closest('.dropdown-item').remove();
            } else {
                alert('Failed to delete.');
            }
        });
        return;
    }

    const item = event.target.closest('.dropdown-item');
    if (!item) return;
    opencode(item.dataset.id);
    openList.style.display = "none";
});

// Opening an Example

examplesButton.onclick = function (event) {
    examplesList.style.display = examplesList.style.display === "none" ? "block" : "none";
};

examplesList.addEventListener('click', function (event) {
    const item = event.target.closest('.dropdown-item');
    if (!item) return;

    const selectedExample = item.dataset.name;
    console.log(`Selected Example : ${selectedExample}`);

    if (examples[selectedExample]) {
        editor.setValue(examples[selectedExample])
    }

    examplesList.style.display = "none"; // close the dropdown
});


//  close dropdown when clicking outside
document.addEventListener('click', function (event) {
    if (!openButton.contains(event.target) && !openList.contains(event.target)) {
        openList.style.display = "none";
    }
});

document.addEventListener('click', function (event) {
    if (!examplesButton.contains(event.target) && !examplesList.contains(event.target)) {
        examplesList.style.display = "none";
    }
});



// Save Button
saveBtn.onclick = async function (event) {
    event.preventDefault();

    if (!isAuthenticated) {
        alert("You have to log in to save, dummy!");
        return;
    }

    // Get code name first
    try {
        const response = await fetch('get_code_name/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        const codeName = data.result;
        console.log('Code Name:', codeName);

        if (!codeName) {
            alert('Create new project first');
            console.log('getCodeName returned Null');
            return;
        }

        // Get code from CodeMirror editor
        const inputCode = editor.getValue();
        console.log('Input code:', inputCode);

        if (!inputCode) {
            alert('Input cannot be empty.');
            return;
        }

        // Save the code
        const saveResponse = await fetch('save_current_code/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: JSON.stringify({
                code_text: inputCode,
                code_name: codeName,
                form_type: 'save_current'
            }),
        });

        if (saveResponse.ok) {
            alert('Code saved successfully!');
        } else {
            const errorText = await saveResponse.text();
            console.log('Error response:', errorText);
            alert('Failed to save code.');
        }

    } catch (error) {
        console.error('Error:', error);
        alert('An unexpected error occurred while saving.');
    }
};

//Dragbar to resize window

const dragbar = document.getElementById("dragbar");
const codeSection = document.querySelector(".code-section");
const mediaSection = document.querySelector(".media-section");
const container = document.querySelector(".container");

let dragging = false;

dragbar.addEventListener("mousedown", () => {
    dragging = true;
});

document.addEventListener("mouseup", () => {
    dragging = false;
});

document.addEventListener("mousemove", (e) => {
    if (!dragging) return;

    const containerWidth = container.offsetWidth;

    let codePercent = (e.clientX / containerWidth) * 100;

    codePercent = Math.max(40, Math.min(80, codePercent));

    codeSection.style.width = `${codePercent}%`;
    mediaSection.style.width = `${100 - codePercent}%`;

    if (window.editor) {
        editor.refresh(); // CodeMirror
    }
});


// toolbar file dropdown

const fileBtn = document.getElementById("file-dropdown-btn");
const fileMenu = document.getElementById("file-dropdown-menu");

fileBtn.addEventListener("click", () => {
    console.log("clicked");
});

fileBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    fileMenu.classList.toggle("show");
});

document.addEventListener("click", (e) => {
    if (
        !fileMenu.contains(e.target) &&
        !fileBtn.contains(e.target)
    ) {
        fileMenu.classList.remove("show");
    }
});

// close dropdown when clicking on any item except those with .has-submenu

document.querySelector(".file-dropdown-menu").addEventListener("click", (e) => {

    if (e.target.closest(".has-submenu")) {
        return; // don't close
    }

    document
        .querySelectorAll(".show")
        .forEach(el => el.classList.remove("show"));
});