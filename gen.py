import hashlib
from PIL import Image, ImageDraw, ImageFont

def words2image(mots, fichier_sortie="mots.png", police="arial.ttf", taille=40, marge=20, largeur_max=800):
    try:
        font = ImageFont.truetype(police, taille)
    except:
        font = ImageFont.load_default()

    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)

    def mesurer_texte(txt):
        bbox = draw.textbbox((0, 0), txt, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Découpage en lignes
    lignes = []
    ligne_courante = []
    largeur_courante = 0

    for mot in mots:
        mot_larg, _ = mesurer_texte(mot)
        espace_larg, _ = mesurer_texte(" ")

        if ligne_courante:
            test_largeur = largeur_courante + espace_larg + mot_larg
        else:
            test_largeur = mot_larg

        if test_largeur <= largeur_max - 2*marge:
            ligne_courante.append(mot)
            largeur_courante = test_largeur
        else:
            lignes.append(ligne_courante)
            ligne_courante = [mot]
            largeur_courante = mot_larg

    if ligne_courante:
        lignes.append(ligne_courante)

    # Taille image
    _, hauteur_ligne = mesurer_texte("Ag")
    largeur_img = largeur_max
    hauteur_img = len(lignes) * (hauteur_ligne + 10) + 2*marge

    img = Image.new("RGB", (largeur_img, hauteur_img), "white")
    draw = ImageDraw.Draw(img)

    positions = []  # positions normalisées
    y = marge

    for i, ligne in enumerate(lignes):
        if i == len(lignes) - 1 or len(ligne) == 1:
            x = marge
            for mot in ligne:
                draw.text((x, y), mot, fill="black", font=font)
                mot_larg, mot_haut = mesurer_texte(mot)
                positions.append({
                    # "word": mot,
                    "x": x / largeur_img,
                    "y": y / hauteur_img,
                    # "largeur": mot_larg / largeur_img,
                    # "hauteur": mot_haut / hauteur_img,
                    "word_part_hash": word2hash(mot)
                })
                x += mot_larg + mesurer_texte(" ")[0]
        else:
            mots_larges = [mesurer_texte(mot)[0] for mot in ligne]
            total_mots = sum(mots_larges)
            espaces = len(ligne) - 1
            espace_total = (largeur_max - 2*marge) - total_mots
            espace_extra = espace_total // espaces
            reste = espace_total % espaces

            x = marge
            for j, mot in enumerate(ligne):
                draw.text((x, y), mot, fill="black", font=font)
                mot_larg, mot_haut = mesurer_texte(mot)
                positions.append({
                    # "word": mot,
                    "x": x / largeur_img,
                    "y": y / hauteur_img,
                    # "largeur": mot_larg / largeur_img,
                    # "hauteur": mot_haut / hauteur_img,
                    "word_part_hash": word2hash(mot)
                })
                if j < espaces:
                    x += mots_larges[j] + espace_extra
                    if j < reste:
                        x += 1
        y += hauteur_ligne + 10

    y = {y:i for i, y in enumerate(sorted(list(set([elm["y"] for elm in positions]))))}
    for elm in positions:
        elm["line"] = y[elm["y"]]

    img.save(fichier_sortie)

    return img, positions, largeur_img, hauteur_img

def word2hash(word:str) -> list[str]:
    wordparts:str = ""
    wordparts_hash:list[str] = []
    for letter in word:
        wordparts += letter
        hash_obj = hashlib.sha256(wordparts.encode())
        wordparts_hash.append(hash_obj.hexdigest())
    return wordparts_hash

def word2letter(word:str) -> list[str]:
    wordparts:str = ""
    wordparts_hash:list[str] = []
    for letter in word:
        wordparts += letter
        wordparts_hash.append(wordparts)
    return wordparts_hash
