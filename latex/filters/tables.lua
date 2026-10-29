-- Render Markdown tables as a booktabs `tabular` inside a `table` float.
-- Pandoc's default `longtable` output does not work in two-column layouts
-- such as IEEEtran or acmart sigconf. Captions are placed above the table, as
-- IEEE, ACM, Springer, and Elsevier require.
-- Row spans are not supported; use a raw LaTeX table for those.

local ALIGN = { AlignLeft = 'l', AlignRight = 'r', AlignCenter = 'c', AlignDefault = 'l' }

local function latex(blocks)
  local out = pandoc.write(pandoc.Pandoc(blocks), 'latex', PANDOC_WRITER_OPTIONS)
  out = out:gsub('\n\n+', ' '):gsub('%s+$', '')
  return out
end

local function row_latex(row)
  local cells = {}
  for _, cell in ipairs(row.cells) do
    local text = latex(cell.contents)
    if cell.col_span > 1 then
      text = string.format('\\multicolumn{%d}{c}{%s}', cell.col_span, text)
    end
    cells[#cells + 1] = text
  end
  return table.concat(cells, ' & ') .. ' \\\\'
end

function Table(tbl)
  local spec = {}
  for _, colspec in ipairs(tbl.colspecs) do
    spec[#spec + 1] = ALIGN[tostring(colspec[1])] or 'l'
  end

  local lines = { '\\begin{table}', '\\centering' }

  local caption = latex(tbl.caption.long)
  local label = tbl.attr.identifier
  if caption ~= '' then
    -- pandoc-crossref may already have put the label into the caption.
    if label ~= '' and not caption:find('\\label{', 1, true) then
      caption = caption .. '\\label{' .. label .. '}'
    end
    lines[#lines + 1] = '\\caption{' .. caption .. '}'
  end

  lines[#lines + 1] = '\\begin{tabular}{' .. table.concat(spec) .. '}'
  lines[#lines + 1] = '\\toprule'
  for _, row in ipairs(tbl.head.rows) do
    lines[#lines + 1] = row_latex(row)
  end
  if #tbl.head.rows > 0 then
    lines[#lines + 1] = '\\midrule'
  end
  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.head) do
      lines[#lines + 1] = row_latex(row)
    end
    for _, row in ipairs(body.body) do
      lines[#lines + 1] = row_latex(row)
    end
  end
  if #tbl.foot.rows > 0 then
    lines[#lines + 1] = '\\midrule'
    for _, row in ipairs(tbl.foot.rows) do
      lines[#lines + 1] = row_latex(row)
    end
  end
  lines[#lines + 1] = '\\bottomrule'
  lines[#lines + 1] = '\\end{tabular}'
  lines[#lines + 1] = '\\end{table}'

  return pandoc.RawBlock('latex', table.concat(lines, '\n'))
end
