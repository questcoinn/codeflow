const MAX_LENGTH = 60;

// 제목을 URL 경로에 쓸 수 있는 slug로 바꾼다.
// 영문은 소문자로, 한글과 숫자는 그대로 두고, 나머지 문자는 하이픈 하나로 합친다.
export function slugify(title: string): string {
  const slug = title
    .normalize('NFC')
    .toLowerCase()
    .replace(/[^a-z0-9가-힣]+/g, '-')
    .replace(/^-+|-+$/g, '');
  if (slug.length <= MAX_LENGTH) return slug;
  return slug.slice(0, MAX_LENGTH).replace(/-+$/, '');
}
