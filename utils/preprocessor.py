"""
Módulo de pré-processamento de logs para o Agente IA de Análise de Logs de Erro.

Este módulo contém funções para:
- Leitura de arquivos de log
- Separação e normalização de mensagens
- Chunking de texto para vetorização
- Extração de metadados dos logs
"""

import re
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple
import tiktoken


class LogPreprocessor:
    """
    Classe responsável pelo pré-processamento de arquivos de log.
    """
    
    def __init__(self, encoding_model: str = "cl100k_base"):
        """
        Inicializa o preprocessador de logs.
        
        Args:
            encoding_model (str): Modelo de encoding para contagem de tokens
        """
        self.encoding = tiktoken.get_encoding(encoding_model)
        self.log_pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(\w+)\s+\[([^\]]+)\]\s+(.*)'
        )
    
    def read_log_file(self, file_path: str) -> str:
        """
        Lê o conteúdo de um arquivo de log.
        
        Args:
            file_path (str): Caminho para o arquivo de log
            
        Returns:
            str: Conteúdo do arquivo de log
            
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
            IOError: Se houver erro na leitura do arquivo
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            print(f"✅ Arquivo de log lido com sucesso: {file_path}")
            return content
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo de log não encontrado: {file_path}")
        except IOError as e:
            raise IOError(f"Erro ao ler arquivo de log: {e}")
    
    def parse_log_entries(self, log_content: str) -> List[Dict]:
        """
        Faz o parsing das entradas de log extraindo metadados.
        
        Args:
            log_content (str): Conteúdo bruto do log
            
        Returns:
            List[Dict]: Lista de dicionários com entradas de log parseadas
        """
        entries = []
        lines = log_content.strip().split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue
                
            match = self.log_pattern.match(line.strip())
            if match:
                timestamp_str, level, component, message = match.groups()
                
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    timestamp = None
                
                entry = {
                    'line_number': line_num,
                    'timestamp': timestamp,
                    'timestamp_str': timestamp_str,
                    'level': level.upper(),
                    'component': component,
                    'message': message,
                    'full_line': line.strip(),
                    'is_error': level.upper() in ['ERROR', 'CRITICAL', 'FATAL']
                }
                entries.append(entry)
            else:
                # Linha que não segue o padrão - pode ser continuação de erro anterior
                if entries:
                    entries[-1]['message'] += f" {line.strip()}"
                    entries[-1]['full_line'] += f" {line.strip()}"
        
        print(f"✅ {len(entries)} entradas de log parseadas com sucesso")
        return entries
    
    def filter_error_entries(self, entries: List[Dict]) -> List[Dict]:
        """
        Filtra apenas as entradas de erro e críticas.
        
        Args:
            entries (List[Dict]): Lista de entradas de log
            
        Returns:
            List[Dict]: Lista filtrada com apenas erros e críticos
        """
        error_entries = [entry for entry in entries if entry['is_error']]
        print(f"✅ {len(error_entries)} entradas de erro identificadas")
        return error_entries
    
    def create_chunks(self, entries: List[Dict], max_tokens: int = 500) -> List[Dict]:
        """
        Cria chunks de texto para vetorização, respeitando limite de tokens.
        
        Args:
            entries (List[Dict]): Lista de entradas de log
            max_tokens (int): Número máximo de tokens por chunk
            
        Returns:
            List[Dict]: Lista de chunks com metadados
        """
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for entry in entries:
            # Calcula tokens da entrada atual
            entry_text = f"{entry['timestamp_str']} {entry['level']} [{entry['component']}] {entry['message']}"
            entry_tokens = len(self.encoding.encode(entry_text))
            
            # Se adicionar esta entrada exceder o limite, finaliza chunk atual
            if current_tokens + entry_tokens > max_tokens and current_chunk:
                chunk_text = "\n".join([e['full_line'] for e in current_chunk])
                chunk = {
                    'chunk_id': len(chunks),
                    'text': chunk_text,
                    'entries': current_chunk.copy(),
                    'token_count': current_tokens,
                    'error_count': sum(1 for e in current_chunk if e['is_error']),
                    'components': list(set(e['component'] for e in current_chunk)),
                    'levels': list(set(e['level'] for e in current_chunk))
                }
                chunks.append(chunk)
                current_chunk = []
                current_tokens = 0
            
            current_chunk.append(entry)
            current_tokens += entry_tokens
        
        # Adiciona último chunk se houver entradas restantes
        if current_chunk:
            chunk_text = "\n".join([e['full_line'] for e in current_chunk])
            chunk = {
                'chunk_id': len(chunks),
                'text': chunk_text,
                'entries': current_chunk.copy(),
                'token_count': current_tokens,
                'error_count': sum(1 for e in current_chunk if e['is_error']),
                'components': list(set(e['component'] for e in current_chunk)),
                'levels': list(set(e['level'] for e in current_chunk))
            }
            chunks.append(chunk)
        
        print(f"✅ {len(chunks)} chunks criados para vetorização")
        return chunks
    
    def extract_error_patterns(self, entries: List[Dict]) -> Dict:
        """
        Extrai padrões comuns de erro para análise.
        
        Args:
            entries (List[Dict]): Lista de entradas de log
            
        Returns:
            Dict: Estatísticas e padrões identificados
        """
        error_entries = self.filter_error_entries(entries)
        
        # Contagem por componente
        component_counts = {}
        for entry in error_entries:
            component = entry['component']
            component_counts[component] = component_counts.get(component, 0) + 1
        
        # Contagem por tipo de erro (palavras-chave)
        error_keywords = {}
        for entry in error_entries:
            message = entry['message'].lower()
            keywords = ['timeout', 'connection', 'failed', 'error', 'exception', 
                       'denied', 'invalid', 'not found', 'unauthorized']
            for keyword in keywords:
                if keyword in message:
                    error_keywords[keyword] = error_keywords.get(keyword, 0) + 1
        
        patterns = {
            'total_errors': len(error_entries),
            'component_distribution': component_counts,
            'error_keywords': error_keywords,
            'time_range': {
                'start': min(e['timestamp'] for e in error_entries if e['timestamp']),
                'end': max(e['timestamp'] for e in error_entries if e['timestamp'])
            } if error_entries else None
        }
        
        print(f"✅ Padrões de erro extraídos: {patterns['total_errors']} erros analisados")
        return patterns
    
    def process_log_file(self, file_path: str, filter_errors_only: bool = True) -> Tuple[List[Dict], Dict]:
        """
        Processa um arquivo de log completo.
        
        Args:
            file_path (str): Caminho para o arquivo de log
            filter_errors_only (bool): Se deve filtrar apenas erros
            
        Returns:
            Tuple[List[Dict], Dict]: Chunks processados e padrões identificados
        """
        print(f"🔄 Iniciando processamento do arquivo: {file_path}")
        
        # Lê o arquivo
        content = self.read_log_file(file_path)
        
        # Faz parsing das entradas
        entries = self.parse_log_entries(content)
        
        # Filtra erros se solicitado
        if filter_errors_only:
            entries = self.filter_error_entries(entries)
        
        # Cria chunks
        chunks = self.create_chunks(entries)
        
        # Extrai padrões
        patterns = self.extract_error_patterns(entries)
        
        print(f"✅ Processamento concluído: {len(chunks)} chunks, {patterns['total_errors']} erros")
        return chunks, patterns


def main():
    """
    Função principal para teste do preprocessador.
    """
    preprocessor = LogPreprocessor()
    
    # Testa com arquivo de exemplo
    log_file = "../data/example.log"
    if os.path.exists(log_file):
        chunks, patterns = preprocessor.process_log_file(log_file)
        
        print("\n📊 Resumo do processamento:")
        print(f"- Total de chunks: {len(chunks)}")
        print(f"- Total de erros: {patterns['total_errors']}")
        print(f"- Componentes com erros: {list(patterns['component_distribution'].keys())}")
        print(f"- Palavras-chave mais comuns: {list(patterns['error_keywords'].keys())}")
    else:
        print(f"❌ Arquivo de exemplo não encontrado: {log_file}")


if __name__ == "__main__":
    main()

