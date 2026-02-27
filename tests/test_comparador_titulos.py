import unittest
from unittest.mock import patch

from comparador_titulos import (
    comparar_titulos,
    main,
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

    def test_cli_falha_quando_argumento_obrigatorio_ausente_sem_interativo(self):
        with self.assertRaises(SystemExit) as exc, patch("comparador_titulos.executar_modo_interativo") as interativo:
            main(["--sistema", "Título presente"])

        self.assertEqual(exc.exception.code, 2)
        interativo.assert_not_called()

    def test_cli_interativo_so_quando_flag_ativada(self):
        with patch("comparador_titulos.executar_modo_interativo", return_value=0) as interativo:
            retorno = main(["--interativo"])

        self.assertEqual(retorno, 0)
        interativo.assert_called_once_with("completo")


if __name__ == "__main__":
    unittest.main()
