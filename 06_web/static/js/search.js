const searchInput = document.querySelector("#machine-search-input");
const suggestBox = document.querySelector("#suggest-box");

if (searchInput && suggestBox) {
    searchInput.addEventListener("input", async () => {
        const q = searchInput.value.trim();

        if (q.length < 1) {
            suggestBox.innerHTML = "";
            suggestBox.style.display = "none";
            return;
        }

        const response = await fetch(`/api/machine_suggest?q=${encodeURIComponent(q)}`);
        const data = await response.json();

        if (data.length === 0) {
            suggestBox.innerHTML = "";
            suggestBox.style.display = "none";
            return;
        }

        suggestBox.innerHTML = data.map(item => `
            <a class="suggest-item" href="/machine?name=${encodeURIComponent(item.machine_name)}">
                <div class="suggest-name">${item.machine_name}</div>
                <div class="suggest-meta">${item.category} / Rank ${item.rank} / Score ${item.score}</div>
            </a>
        `).join("");

        suggestBox.style.display = "block";
    });
}