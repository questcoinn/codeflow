import { slugify } from './utils/slugify';

const input = document.querySelector<HTMLInputElement>('#title')!;
const output = document.querySelector<HTMLElement>('#slug')!;
input.addEventListener('input', () => {
  output.textContent = slugify(input.value);
});
