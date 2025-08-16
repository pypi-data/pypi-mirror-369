from regex import search, compile, purge, Pattern, escape, findall
from unicodedata import name
from immutableType import Str_, Bool_, Int_

class Find:

    def __init__(self):
        """
        Init all characters.
        """

        self.__alphabet_avec_variantes = {}
        self.__trouver_variantes_de_lettre()

        self.__in_word: Bool_ = Bool_(False)


    def __trouver_variantes_de_lettre(self) -> None:
        """
        Trouves des variantes de toutes les lettres et ajoute la ponctuation et les caractères digitaux
        :return:
        """
        pattern = compile(r"\b([a-zA-Z])\b")  # Modèle pour trouver les lettres de base
        for codepoint in range(0x110000):  # Limite de l'espace Unicode
            char = chr(codepoint)
            try:
                # Vérifier si le nom du caractère contient la lettre de base "a"
                unicode_name = name(char)

                result = search(pattern, unicode_name)

                if result is not None:
                    result_group1 = result.group(1).lower()  # Convertir en minuscule
                    char = escape(char)
                    if result_group1 not in self.__alphabet_avec_variantes:
                        self.__alphabet_avec_variantes[result_group1] = [char]
                    else:
                        self.__alphabet_avec_variantes[result_group1].append(char)

            except ValueError:
                # Ignorer les caractères qui n'ont pas de nom Unicode
                pass


    def __recherche_regex(self, mot: str) -> Pattern:
        """
        Crée le patter correspondant au mot recherché
        :param mot: le mot recherché
        :return: un modèle regex
        """
        correspondances = []

        for i in mot:
            correspondances.append(self.__alphabet_avec_variantes[i])

        pattern = r''.join([r"[^\p{L}]*(?:" + rf"([{''.join(sous_liste)}])+?|" + r"[^\p{L}]+?)[^\p{L}]*" for sous_liste in correspondances])  # ne marche pas. prend toujours 'on pour "con"
        return compile(self.__modifier_pattern(pattern))

    def __modifier_pattern(self, pattern) -> str:
        """
        Modifie le modèle avec les choix de l'utilisateur
        :param pattern: le modèle de base construit par __recherche_regex
        :return: le modèle
        """
        if not self.__in_word:
            pattern = rf"\b(?:{pattern})\b"

        return pattern



    def __find_all_iteration(self, word: str,  sentence: str, regex: Pattern, sensitive: int) -> bool:
        """
        Concatène chaque mot un à un pour vérifier le match.
        :param word:
        :param sentence:
        :param regex:
        :return:
        """

        if not sentence:
            return None # Retourner None si le mot n'est pas trouvé dans la phrase entière

        result = findall(regex, sentence)

        if not result:
            return False

        # calcule le pourcentage de correspondance
        for match in result:
            p = 100
            for i in match:
                if not i:
                    p -= 100 / len(match)

            if p < sensitive:
                return False

        return True  # Retourner True si le pourcentage est supérieur à la sensibilité



    def find_Badwords(self, word: str, sentence: str, in_word: bool = False, sensitive: int = 40) -> bool:
        """
        Search any configuration of word in the sentence
        :param word: a simple word write in LATIN (not string digit) EX : ``ass`` not ``a*s``
        :param sentence: the sentence who the word is find (or not)
        :param sensitive: the sensitivity of the search, from 0 to 100, default is 40
        :param in_word: Allow research word in another word
        :return: ``True`` if the word is find, else ``False``
        """

        wordStr = Str_(word)
        sentenceStr = Str_(sentence)
        sensitiveInt = Int_(sensitive)
        self.__in_word.bool_ = in_word

        regex = self.__recherche_regex(wordStr.str_)

        result = self.__find_all_iteration(wordStr.str_, sentenceStr.str_, regex, sensitiveInt.int_)

        purge()
        return result
