const shareBtn = document.getElementById("share-btn");
const shareModal = document.getElementById("share-modal");
const shareClose = document.getElementById("share-close");

const publicToggle =
    document.getElementById("public-toggle");

const shareUrl =
    document.getElementById("share-url");

const shareUrlSection =
    document.getElementById("share-url-section");

const privateMessage =
    document.getElementById("private-message");

const copyBtn =
    document.getElementById("copy-share-link");


// Open modal to Share Code
shareBtn.addEventListener("click", async () => {

    const response = await fetch("get-share-url/");
    const data = await response.json();

    if (data.no_code_id) {
        alert(data.no_code_id);
        return;
    }

    if (data.error) {
        alert(data.error);
        return;
    }

    shareUrl.value = data.url;

    publicToggle.checked = data.is_public;

    updateShareUI();

    shareModal.style.display = "block";
});


// Close button
shareClose.addEventListener("click", () => {
    shareModal.style.display = "none";
});


// Click outside modal
window.addEventListener("click", (e) => {

    if (e.target === shareModal) {
        shareModal.style.display = "none";
    }

});


// Copy URL
copyBtn.addEventListener("click", async () => {

    await navigator.clipboard.writeText(
        shareUrl.value
    );

    copyBtn.textContent = "✓";

    setTimeout(() => {
        copyBtn.textContent = "📋";
    }, 1000);

});


// Public toggle
publicToggle.addEventListener("change", async () => {

    const response = await fetch(
        "set-project-visibility/",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                is_public: publicToggle.checked
            })
        }
    );

    const data = await response.json();

    if (data.status === "success") {
        updateShareUI();
    }
});


// Show / hide URL section
function updateShareUI() {

    console.log("toggle:", publicToggle.checked);

    if (publicToggle.checked) {

        shareUrlSection.style.display = "block";

        privateMessage.style.display = "none";

    } else {

        shareUrlSection.style.display = "none";

        privateMessage.style.display = "block";
    }
}
