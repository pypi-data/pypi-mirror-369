from re import search, compile, purge, Pattern
from string import punctuation, ascii_lowercase, digits
from unicodedata import name
from immutableType import Str_, Bool_, StrError

special_caracteres = punctuation+digits+' '

class Find:

    def __init__(self):
        """
        Init all characters.
        THE INITIALISATION IS VERY SLOW !
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
        l = list(special_caracteres)
        for codepoint in range(0x110000):  # Limite de l'espace Unicode
            char = chr(codepoint)
            try:
                # Vérifier si le nom du caractère contient la lettre de base "a"
                unicode_name = name(char)

                result = search(pattern, unicode_name)

                if result is not None:
                    result_group1 = result.group(1).lower()  # Convertir en minuscule
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

        pattern = r''.join([rf"[{''.join(sous_liste)}]+[{special_caracteres}]*" for sous_liste in correspondances])  # ne marche pas. prend toujours 'on pour "con"


        return compile(self.__modifier_pattern(pattern))

    def __modifier_pattern(self, pattern) -> str:
        """
        Modifie le modèle avec les choix de l'utilisateur
        :param pattern: le modèle de base construit par __recherche_regex
        :return: le modèle
        """
        if not self.__in_word:
            pattern = rf"\b{pattern}\b"
            print(pattern)

        return pattern



    def __find_all_iteration(self, sentence: str, regex: Pattern):
        """
        Concatène chaque mot un à un pour vérifier le match
        :param word:
        :param sentence:
        :param regex:
        :return:
        """

        if sentence == '':
            return None # Retourner None si le mot n'est pas trouvé dans la phrase entière

        result = search(regex, sentence)

        print(result)



    def find_Badwords(self, word: str, sentence: str, linebreak: bool = True, in_word: bool = False) -> bool:
        """
        Search any configuration of word in the sentence
        :param word: a simple word write in LATIN (not string digit) EX : ``ass`` not ``a*s``
        :param sentence: the sentence who the word is find (or not)
        :param linebreak: Replace \\n by space
        :param in_word: Allow research word in another word
        :return: ``True`` if the word is find, else ``False``
        """

        wordStr = Str_(word)
        sentenceStr = Str_(sentence)
        linebreakBool = Bool_(linebreak)
        self.__in_word.bool_ = in_word

        regex = self.__recherche_regex(wordStr.str_)

        if linebreakBool:
            u = sentenceStr.str_.split('\n')
            sentenceStr.str_ = ' '.join(u)

        result = self.__find_all_iteration(sentenceStr.str_, regex)

        if result is None:
            purge()
            return False

        # si la phrase ne contient que des caractères spéciaux
        x = 0
        for i in result.group():
            if i in special_caracteres:
                x += 1

        # on ne fait rien
        if len(result.group()) == x:
            return False

        purge()
        return True
