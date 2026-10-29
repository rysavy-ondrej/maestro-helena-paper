-- Add the \Description{...} that acmart requires for accessible figures,
-- using the figure caption as plain text. Figures written as raw LaTeX
-- need their own \Description.

local SPECIAL = {
  ['\\'] = '\\textbackslash{}', ['{'] = '\\{', ['}'] = '\\}', ['%'] = '\\%',
  ['&'] = '\\&', ['#'] = '\\#', ['_'] = '\\_', ['$'] = '\\$',
  ['^'] = '\\^{}', ['~'] = '\\~{}',
}

local function escape(text)
  return (text:gsub('[\\{}%%&#_$^~]', SPECIAL))
end

function Figure(fig)
  -- Math becomes its source without backslashes: $\tau_c$ -> tau_c.
  local caption = fig.caption.long:walk {
    Math = function(m) return pandoc.Str((m.text:gsub('\\', ''))) end,
  }
  local text = pandoc.utils.stringify(caption)
  local first = fig.content[1]
  -- Append inline to the image's block: an extra block would turn the figure
  -- into side-by-side subfigures.
  if text ~= '' and first and (first.t == 'Plain' or first.t == 'Para') then
    first.content:insert(pandoc.RawInline('latex', '\\Description{' .. escape(text) .. '}'))
  end
  return fig
end
