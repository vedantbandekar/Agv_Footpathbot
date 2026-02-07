//javascript
const menuBtn = document.getElementById("menu-btn");
const sidebar = document.getElementById("sidebar");

menuBtn.addEventListener("click", () => {
  sidebar.classList.toggle("open");
});

function openModal(src) {
  const modal = document.getElementById("imageModal");
  const modalImg = document.getElementById("modalImage");

  modal.style.display = "flex";
  modalImg.src = src;
}

function closeModal() {
  document.getElementById("imageModal").style.display = "none";
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeModal();
});


function filterByTag(tag) {
  const cards = document.querySelectorAll(".dataset-card");

  cards.forEach(card => {
    const cardTag = card.dataset.tag;

    if (tag === "All" || cardTag === tag) {
      card.classList.remove("hidden");
    } else {
      card.classList.add("hidden");
    }
  });
}

function saveTag(button) {
  const card = button.closest(".dataset-card");
  const input = card.querySelector(".tag-input");
  const badge = card.querySelector(".tag-badge");
  const editBtn = card.querySelector(".edit-tag");

  const label = input.value.trim();
  const imageId = input.dataset.id;

  if (!label) return;

  fetch("/update_label", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image_id: imageId, label: label })
  }).then(() => {
    input.classList.add("hidden");
    button.classList.add("hidden");

    badge.textContent = label;
    badge.classList.remove("hidden");

    editBtn.classList.remove("hidden");
  });
}

function editTag(button) {
  const card = button.closest(".dataset-card");
  const input = card.querySelector(".tag-input");
  const saveBtn = card.querySelector("button[onclick='saveTag(this)']");
  const badge = card.querySelector(".tag-badge");

  badge.classList.add("hidden");
  button.classList.add("hidden");

  input.classList.remove("hidden");
  saveBtn.classList.remove("hidden");

  input.focus();
}