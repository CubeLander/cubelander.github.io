# Publish technical notes with traceable evidence

Enter when turning BetterScale material into articles or publishing this blog.
Read the root README for commands, content fields and deployment ownership.

## Source identity before links

The supplied BetterScale checkout's HEAD was not present in either public GitHub
repository when this site was first built. Do not blindly construct public links
from a local SHA. Public `vLLM-HUST/BetterScale` snapshot
`872b4133dd76c999b5709d52643cdac2602374f7` contains the chosen evidence; Git blob
identity matched the supplied REPORT, E2E-20260914, CAPACITY-0.4 and RESULTS files.
All other article source paths were checked against that snapshot's public tree.
Future material needs its own verified source identity, not an assumed reuse of
this observation. Source checkout reads are read-only; do not publish local notes
or source Git history as part of the website.

The historical REPORT uses the retired `strengthen_dsv4` package and older
configuration envelope. Explain its mechanisms as historical evidence; use
current package docs if explicitly adding installation instructions. Preserve
run155's reused DP result / later 0.3.1 integration distinction. Never promote
32 retrieval questions to a full-suite quality claim, dummy capacity to semantic
quality, or matched cycles to endpoint throughput.

## Build and preview boundaries

Markdown uses `markdownTemplateEngine: false` to avoid evaluating article prose
as templates. Dynamic permalinks therefore use a JavaScript data function in
`src/posts/posts.11tydata.js`, not a literal Nunjucks string in JSON.

`npm run dev` builds then serves `_site` using Python on 127.0.0.1:8080. This is
not a watch server: rebuild and refresh after editing. Eleventy's CLI does not
support `--host`; do not reintroduce that flag. Current build-only dependency
advisories and their scope are in README; they are not declared fixed.

`npm test` checks generated structure, internal links and Markdown exports.
Also inspect home and an article at desktop and phone widths when changing CSS.
Tables must scroll inside the article, not force the entire mobile page wider.

## Publication

Repository: CubeLander/cubelander.github.io (public, owned by CubeLander).
SSH remote: git@github.com:CubeLander/cubelander.github.io.git.
Pages uses the Actions workflow, not a branch source. Push main, wait for the
specific workflow run, then verify the public HTTPS site. Do not equate an
accepted push with a completed deployment. There is no PR or release-message
requirement for ordinary direct publication.
