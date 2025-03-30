import os
import requests
import pandas as pd
import tabula
import zipfile
import csv
from bs4 import BeautifulSoup
import logging
import re
from unicodedata import normalize

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ans_processor.log'),
        logging.StreamHandler()
    ]
)

class ANSProcessor:
    def __init__(self):
        self.base_url = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
        self.download_dir = "downloads"
        self.output_dir = "output"
        self.abbreviations = {
            'OD': 'Seg. Odontológica',
            'AMB': 'Seg. Ambulatorial'
        }
        self.expected_columns = [
            'PROCEDIMENTO', 'RN_alteracao', 'VIGENCIA', 'Seg. Odontológica', 'Seg. Ambulatorial',
            'HCO', 'HSO', 'REF', 'PAC', 'DUT', 'SUBGRUPO',
            'GRUPO', 'CAPITULO'
        ]

    def _create_directories(self):
        """Cria os diretórios necessários para o processamento"""
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def _download_file(self, url: str, filename: str) -> str:
        """Baixa um arquivo da URL especificada"""
        local_path = os.path.join(self.download_dir, filename)
        
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            logging.info(f"Arquivo baixado: {local_path}")
            return local_path
        except Exception as e:
            logging.error(f"Erro ao baixar {url}: {str(e)}")
            raise

    def find_anexo_i_url(self) -> str:
        """Encontra a URL do Anexo I no portal da ANS"""
        try:
            response = requests.get(self.base_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'Anexo_I' in href and (href.lower().endswith('.pdf') or href.lower().endswith('.xlsx')):
                    logging.info(f"URL do Anexo I encontrada: {href}")
                    return href if href.startswith('http') else f"https://www.gov.br{href}"
            
            raise Exception("URL do Anexo I não encontrada")
        except Exception as e:
            logging.error(f"Erro ao buscar URL: {str(e)}")
            raise

    def extract_tables_from_pdf(self, pdf_path: str) -> pd.DataFrame:
        """Extrai tabelas de um arquivo PDF"""
        try:
            logging.info("Iniciando extração de tabelas do PDF...")
            
            tables = tabula.read_pdf(
                pdf_path,
                pages='all',
                multiple_tables=True,
                lattice=True,
                pandas_options={'header': None},
                encoding='utf-8',
                silent=True
            )
            
            processed_tables = []
            for table in tables:
                if len(table.columns) > 3:
                    table = table.dropna(axis=1, how='all')
                    new_header = table.iloc[0]
                    table = table[1:]
                    table.columns = new_header
                    processed_tables.append(table)
            
            if not processed_tables:
                raise ValueError("Nenhuma tabela válida encontrada no PDF")
            
            full_table = pd.concat(processed_tables, ignore_index=True)
            
            if len(full_table.columns) < len(self.expected_columns):
                raise ValueError(f"O número de colunas extraídas ({len(full_table.columns)}) é menor que o esperado ({len(self.expected_columns)})")
            
            logging.info(f"Extraídas {len(full_table)} linhas")
            return full_table
        except Exception as e:
            logging.error(f"Erro na extração do PDF: {str(e)}")
            raise

    def normalize_text(self, text: str) -> str:
        """Normaliza texto removendo caracteres especiais e múltiplos espaços"""
        if not isinstance(text, str):
            return text
            
        text = normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
        text = re.sub(r'[^\w\s,.;-]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        return text

    def _replace_abbreviations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Substitui abreviações pelos valores completos"""
        for col, full_name in self.abbreviations.items():
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: full_name if str(x).strip().upper() == col else x
                )
        return df

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpa e formata o DataFrame antes de salvar"""
        try:
            logging.info("Limpando e formatando dados...")
            
            df = df.dropna(how='all')
            df.columns = [self.normalize_text(col) for col in df.columns]
            
            if len(df.columns) > len(self.expected_columns):
                df = df.iloc[:, :len(self.expected_columns)]
            
            df.columns = self.expected_columns[:len(df.columns)]
            
            # Aplica a substituição das abreviações
            df = self._replace_abbreviations(df)
            
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str).apply(self.normalize_text)
                df[col] = df[col].replace({'nan': '', 'None': '', 'NaT': ''})
            
            df = df.fillna('')
            
            logging.info("Dados limpos e formatados")
            return df
        except Exception as e:
            logging.error(f"Erro na limpeza dos dados: {str(e)}")
            raise

    def save_to_csv(self, df: pd.DataFrame, filename: str) -> str:
        """Salva o DataFrame em CSV com formatação adequada"""
        try:
            csv_path = os.path.join(self.output_dir, filename)
            
            df.to_csv(
                csv_path,
                index=False,
                encoding='utf-8-sig',
                sep=';',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL,
                lineterminator='\n'
            )
            
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
            
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if line:
                    cleaned_lines.append(line + '\n')
            
            with open(csv_path, 'w', encoding='utf-8-sig') as f:
                f.writelines(cleaned_lines)
            
            logging.info(f"CSV formatado corretamente salvo em: {csv_path}")
            return csv_path
        except Exception as e:
            logging.error(f"Erro ao salvar CSV: {str(e)}")
            raise

    def create_zip(self, csv_path: str, zip_name: str) -> str:
        """Cria um arquivo ZIP contendo o CSV processado"""
        try:
            zip_path = os.path.join(self.output_dir, zip_name)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(csv_path, os.path.basename(csv_path))
            
            logging.info(f"Arquivo ZIP criado: {zip_path}")
            return zip_path
        except Exception as e:
            logging.error(f"Erro ao criar ZIP: {str(e)}")
            raise

    def process(self, seu_nome: str):
        """Executa o pipeline completo"""
        try:
            self._create_directories()
            
            pdf_url = self.find_anexo_i_url()
            pdf_path = self._download_file(pdf_url, "Anexo_I.pdf")
            
            df = self.extract_tables_from_pdf(pdf_path)
            df_cleaned = self.clean_dataframe(df)
            
            csv_path = self.save_to_csv(df_cleaned, "Rol_Procedimentos.csv")
            
            zip_name = f"Teste_{seu_nome}.zip"
            zip_path = self.create_zip(csv_path, zip_name)
            
            logging.info(f"Processo concluído com sucesso! Arquivo final: {zip_path}")
            return zip_path
        except Exception as e:
            logging.error(f"Falha no processamento: {str(e)}")
            raise


if __name__ == "__main__":
    processor = ANSProcessor()
    processor.process("Ana_Perini")