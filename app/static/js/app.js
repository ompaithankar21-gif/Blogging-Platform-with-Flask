document.querySelectorAll('.rich-toolbar button').forEach((button) => {
    button.addEventListener('click', () => {
        const value = button.dataset.value || null;
        document.execCommand(button.dataset.command, false, value);
    });
});

const editor = document.querySelector('.rich-editor');
const postForm = document.querySelector('#post-form');
if (editor && postForm) {
    postForm.addEventListener('submit', () => {
        const content = postForm.querySelector('[name="content"]');
        content.value = editor.innerHTML;
    });
}
