document.querySelectorAll(".dropdown-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
        e.stopPropagation();

        const menuId = btn.dataset.dropdown;
        const menu = document.getElementById(menuId);

        document.querySelectorAll(".dropdown-menu").forEach(m => {
            if (m !== menu) {
                m.classList.remove("show");
            }
        });

        menu.classList.toggle("show");
    });
});

document.addEventListener("click", () => {
    document.querySelectorAll(".dropdown-menu").forEach(menu => {
        menu.classList.remove("show");
    });
});







const deleteBtn = document.getElementById("delete-account-btn");

if (deleteBtn) {
    deleteBtn.addEventListener("click", () => {

        const confirmed = confirm(
            "Are you sure you want to permanently delete your account?"
        );

        if (confirmed) {
            fetch("/delete-account/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": "{{ csrf_token }}"
                }
            })
                .then(() => {
                    alert("Account deleted");
                    window.location.href = "/";
                });
        }
    });
}