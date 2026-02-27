import unittest

from comparador_titulos import (
    comparar_titulos,
    normalizar_texto_para_comparacao,
    normalizar_texto_para_exibicao,
)


class ComparadorTitulosTests(unittest.TestCase):
    def test_normalizacao_compactada_remove_acento_e_simbolo(self):
        texto = "Título: Projeto Ágil #1"
        self.assertEqual(normalizar_texto_para_comparacao(texto), "tituloprojetoagil1")

    def test_normalizacao_exibicao_mantem_espacos(self):
        texto = "Título:   Projeto   Ágil #1"
        self.assertEqual(normalizar_texto_para_exibicao(texto), "titulo projeto agil 1")

    def test_comparacao_igual_com_variacoes_de_formatacao(self):
        s = "Título do Projeto"
        p = "titulo-do projeto!!!"
        resultado = comparar_titulos(s, p)
        self.assertTrue(resultado.sao_iguais)
        self.assertIsNone(resultado.primeira_diferenca_indice)

    def test_comparacao_diferente_encontra_diferencas(self):
        s = "Sistema de Gestão Escolar"
        p = "Sistema Escolar"
        resultado = comparar_titulos(s, p)
        self.assertFalse(resultado.sao_iguais)
        self.assertIsNotNone(resultado.primeira_diferenca_indice)
        self.assertGreaterEqual(len(resultado.diferencas), 1)


if __name__ == "__main__":
    unittest.main()
