import { mkdirSync, writeFileSync } from 'node:fs';

export default function (config) {
  let articles = [];
  config.addPassthroughCopy('src/assets');
  config.addPassthroughCopy({ 'public/taxi': 'taxi' });
  config.addPassthroughCopy('src/robots.txt');
  config.addFilter('newestFirst', posts => [...posts].sort((a, b) => b.date - a.date));
  config.addFilter('iso', date => new Date(date).toISOString().slice(0, 10));
  config.addFilter('readTime', text => Math.max(1, Math.ceil(text.replace(/<[^>]*>/g, '').length / 450)));
  config.addFilter('json', value => JSON.stringify(value).replace(/</g, '\\u003c'));
  config.addCollection('articles', api => {
    articles = api.getFilteredByTag('post').sort((a, b) => a.data.order - b.data.order);
    return articles;
  });
  config.on('eleventy.after', ({ results }) => {
    mkdirSync('_site/text', { recursive: true });
    for (const result of results.filter(r => r.inputPath.startsWith('./src/posts/') && r.inputPath.endsWith('.md'))) {
      const post = articles.find(p => p.inputPath === result.inputPath);
      const slug = result.inputPath.split('/').pop();
      const raw = post.rawInput.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, '');
      const links = post.data.sources.map(source => `- [${source.label}](https://github.com/vLLM-HUST/BetterScale/blob/${post.data.snapshot}/${source.path})`).join('\n');
      writeFileSync(`_site/text/${slug}`, `# ${post.data.title}\n\n发布日期：${new Date(post.date).toISOString().slice(0, 10)}\n\n${raw}\n## 来源与版本\n\n${links}\n`);
    }
    writeFileSync('_site/.nojekyll', '');
  });
  return { dir: { input: 'src', output: '_site' }, markdownTemplateEngine: false, htmlTemplateEngine: 'njk' };
}
