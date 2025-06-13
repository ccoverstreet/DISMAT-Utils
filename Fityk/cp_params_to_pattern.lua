prev_y = nil
for n = 1, 1 do
  	local path = F:get_info(“filename”, n)
  	local filename = string.match(path, “[^/\\\\]+$“) or “”
  	F:execute(string.format(“@%d.F = copy(@%d.F)“, n, n-1))
  	F:execute(string.format(“fit @%d”, n))
end
