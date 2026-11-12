# Derived data

`lp2_runes.csv`: one row per rune on LP2 pages 17-72 (12,956 runes), read from the page images by `lpswarm.pageimages` and aligned to the
manifest sections 10-25 (`python -m lpswarm.lp_table`). Columns: global index, page, line, position in line, rune id and token, the word
separator the image shows after it (`none`, `word`, `colon`), whether the scream314 text has a word break there, red/black, drop cap,
terminator (dotted red square after it), manifest section and position in it. It differs from the scream314 text at one rune (global 5891,
page 41 line 8: the image shows AE, the text has A). The page images are not committed; their SHA-256 sums are in `data/lp_images.sha256`.

## tokens_66_68.csv
The 256 two-character tokens (columns index, page, row, col, token) on images 66, 67 and 68, read from the page images by `python -m lpswarm.research_tokens read`
(shape groups labelled by eye; see the module docstring). A token is a digit 0-4 and a digit or letter; read as base 62 in the order 0-9A-Za-z the values run 0 to 263.
