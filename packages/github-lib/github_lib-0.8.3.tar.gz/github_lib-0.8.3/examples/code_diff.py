import code_diff as cd

# https://github.com/janeczku/calibre-web/commit/7ad419dc8c12180e842a82118f4866ac3d074bc5#diff-df2763da4d356e23778575960aec009432712120b5576ee8d3bfacc8b7c63eabR262

hunk_1_old_line = '    $("#upload-format").html(filename);'
hunk_1_new_line = '    $("#upload-format").text(filename);'

output = cd.difference(hunk_1_old_line, hunk_1_new_line, lang="javascript")

print(output)
ast_changes = output.edit_script()

for el in ast_changes:
    print(el)

hunk_2_old_line = '    $("#upload-cover").html(filename);'
hunk_2_new_line = '    $("#upload-cover").text(filename);'

output_2 = cd.difference(hunk_2_old_line, hunk_2_new_line, lang="javascript")

print(output)
ast_changes_2 = output_2.edit_script()

for el in ast_changes_2:
    print(el)
