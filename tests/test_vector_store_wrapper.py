import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
import dotenv
import qdrant_client
from qdrant_client.models import Distance, VectorParams
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import Qdrant

# テスト対象のモジュールをインポート
from weather_concierge.chains.vector_store_wrapper import (
    load_qdrant,
    build_vector_store,
    read_files_with_metadata,
)  # 実際のモジュール名に置き換えてください


class TestVectorStore(unittest.TestCase):
    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "test_api_key",
            "OPENAI_API_BASE": "test_api_base",
            "QDRANT_HOST": "test_host",
        },
    )
    @patch("qdrant_client.QdrantClient")
    @patch("langchain_openai.OpenAIEmbeddings")
    def test_load_qdrant(self, mock_embeddings, mock_qdrant_client):
        # モックの設定
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client
        mock_client.get_collections.return_value.collections = []

        # 関数の実行
        result = load_qdrant()

        # アサーション
        self.assertIsInstance(result, Qdrant)
        mock_qdrant_client.assert_called_once_with(host="test_host", port=6333)
        mock_client.create_collection.assert_called_once()
        mock_embeddings.assert_called_once_with(
            openai_api_key="test_api_key", openai_api_base="test_api_base"
        )

    @patch("your_module_name.load_qdrant")
    def test_build_vector_store(self, mock_load_qdrant):
        # モックの設定
        mock_qdrant = MagicMock()
        mock_load_qdrant.return_value = mock_qdrant

        # テストデータ
        test_texts = ["test text 1", "test text 2"]
        test_metadatas = [{"source": "test1"}, {"source": "test2"}]

        # 関数の実行
        build_vector_store(test_texts, test_metadatas)

        # アサーション
        mock_qdrant.add_texts.assert_called_once_with(
            texts=test_texts, metadatas=test_metadatas
        )

    def test_read_files_with_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            # テスト用のファイルを作成
            with open(os.path.join(tmpdirname, "test.txt"), "w") as f:
                f.write("This is a test file.")

            # 関数の実行
            texts, metadatas = read_files_with_metadata(tmpdirname)

            # アサーション
            self.assertEqual(len(texts), 1)
            self.assertEqual(len(metadatas), 1)
            self.assertIn("This is a test file.", texts[0])
            self.assertIn("DocumentID", metadatas[0])
            self.assertIn("source", metadatas[0])


if __name__ == "__main__":
    unittest.main()
