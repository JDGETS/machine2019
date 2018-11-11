# machine2019

### Commande pour stream camera sur Raspberry Pi:
``` Bash
raspivid -n -fps 30 -vs -w 683 -h 384 -md 4 -o - -t 1000000 | nc -l 2222
```

### Splitter de stream sur les ordi: 
``` Bash
nc raspberrypi-rose 2222 | tee >(nc -l 2222) | nc -l 2223
```


### Commande pour générer la matrice de correction des lentilles

Commencer par prendre environ 50 photos avec le script suivant. La résolution doit être adapté à celle qui sera utilisé lors de la compétition.
```
python save_snapshots.py --dwidth 1280 --dheight 720 --raspi True
```

Prendre tous les fichers des photo et les déplacer dans un nouveau dossier.

Génerer la matrice avec le script suivant. Il faut que les paramètres soient : dossier_image, type de fichier, largeur en nombre de carré du chessboard, longeur en nombre de carré du chessboard et longeur d'un carré en mm.
```
python cameracalib.py dossier_image jpg 7 5 34
```

Voici le lien du tutoriel qui a fait les scripts :https://www.youtube.com/watch?v=QV1a1G4lL3U

### Fonction opencv en python pour utiliser la matrice

Define camera matrix K
K = np.array([[673.9683892, 0., 343.68638231],
              [0., 676.08466459, 245.31865398],
              [0., 0., 1.]])

Define distortion coefficients d
d = np.array([5.44787247e-02, 1.23043244e-01, -4.52559581e-04, 5.47011732e-03, -6.83110234e-01])

Read an example image and acquire its size
img = cv2.imread("calibration_samples/2016-07-13-124020.jpg")
h, w = img.shape[:2]

Generate new camera matrix from parameters
newcameramatrix, roi = cv2.getOptimalNewCameraMatrix(K, d, (w,h), 0)

Generate look-up tables for remapping the camera image
mapx, mapy = cv2.initUndistortRectifyMap(K, d, None, newcameramatrix, (w, h), 5)

Remap the original image to a new image
newimg = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)

Example d'un script : https://hackaday.io/project/12384-autofan-automated-control-of-air-flow/log/41862-correcting-for-lens-distortions





