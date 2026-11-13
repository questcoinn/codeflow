import { test } from 'node:test';
import assert from 'node:assert/strict';
import { slugify } from '../src/utils/slugify.ts';

test('영문 대문자는 소문자로 바꾸고 공백은 하이픈으로 바꾼다', () => {
  assert.equal(slugify('Hello World'), 'hello-world');
});

test('한글과 숫자는 그대로 둔다', () => {
  assert.equal(slugify('2024년 회고'), '2024년-회고');
});

test('연속된 공백과 기호는 하이픈 하나로 합친다', () => {
  assert.equal(slugify('React  &  Vue!!  비교'), 'react-vue-비교');
});

test('앞뒤의 공백과 기호는 하이픈으로 남기지 않는다', () => {
  assert.equal(slugify('  [공지] 점검 안내!  '), '공지-점검-안내');
});

test('기호만 있는 제목은 빈 문자열이 된다', () => {
  assert.equal(slugify('!!! ???'), '');
});

test('자모가 분리된(NFD) 한글도 완성형 한글로 합쳐서 남긴다', () => {
  // macOS 등에서 붙여넣은 제목은 '한글'이 초성·중성·종성 코드로 나뉘어 들어올 수 있다.
  const decomposedHangul = '\u1112\u1161\u11ab\u1100\u1173\u11af';
  assert.equal(slugify(decomposedHangul), '한글');
});

test('60자를 넘는 slug는 60자로 자른다', () => {
  const title = 'a'.repeat(61);
  assert.equal(slugify(title), 'a'.repeat(60));
});

test('60자에서 자른 끝이 하이픈이면 그 하이픈을 지운다', () => {
  // slug는 'a' 59개 + '-' + 'b'(61자)이므로, 60자에서 자르면 하이픈으로 끝난다.
  const title = 'a'.repeat(59) + ' b';
  assert.equal(slugify(title), 'a'.repeat(59));
});
