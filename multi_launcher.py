local_file = open('localip.txt','r').read().split('\n')
if str.isdigit(local_file[0][-1]):
	if int(local_file[0][-1]) >= 3:
		local_file[0] = local_file[0][:-1] + str(0)
	else:
		local_file[0] = local_file[0][:-1] + str(int(local_file[0][-1]) + 1)
else:
	local_file[0] = local_file[0] + str(1)

open('localip.txt','w').write('\n'.join(local_file))

import game