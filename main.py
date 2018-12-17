import sys
sys.path.insert(0, 'src')

import config
import doggo
import pupper


if sys.argv[1] == 'doggo':
    doggo.main()
elif sys.argv[1] == 'pupper':
    pupper.main()

