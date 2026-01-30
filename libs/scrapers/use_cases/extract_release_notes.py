"""
Use Case - Extract Release Notes

Caso de uso especializado para extração de notas de versão.
Adiciona lógica específica para release notes além do scraping comum.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from libs.scrapers.domain import Document, ScrapingResult, DocumentType
from libs.scrapers.ports import IDocumentScraper, IDocumentRepository


class ExtractReleaseNotes:
    """
    Use Case: Extract Release Notes
    
    Especialização do scraping para notas de versão:
    1. Identifica URLs de release notes
    2. Extrai versões individuais (âncoras)
    3. Organiza por módulo e versão
    4. Gera metadados específicos de release notes
    
    Adiciona lógica de negócio específica para release notes
    além do scraping genérico.
    """
    
    def __init__(
        self,
        scraper: IDocumentScraper,
        repository: IDocumentRepository,
    ):
        """
        Inicializa use case.
        
        Args:
            scraper: Scraper que suporta release notes
            repository: Repositório para persistir
        """
        self.scraper = scraper
        self.repository = repository
    
    async def execute(
        self,
        release_notes_urls: List[str],
        save_to_repository: bool = True,
    ) -> ScrapingResult:
        """
        Extrai release notes de múltiplas URLs.
        
        Args:
            release_notes_urls: URLs de páginas de release notes
            save_to_repository: Se True, salva documentos
        
        Returns:
            ScrapingResult: Resultado com release notes extraídas
        """
        started_at = datetime.now()
        documents: List[Document] = []
        errors: List[str] = []
        warnings: List[str] = []
        successful = 0
        failed = 0
        
        for url in release_notes_urls:
            try:
                # Scrape release notes
                result = await self.scraper.scrape_all(url)
                
                # Filtrar apenas release notes
                release_notes = [
                    doc for doc in result.documents
                    if doc.doc_type == DocumentType.RELEASE_NOTE
                ]
                
                if not release_notes:
                    warnings.append(f"No release notes found at {url}")
                    continue
                
                # Enriquecer metadados
                for doc in release_notes:
                    enriched = self._enrich_release_note(doc)
                    documents.append(enriched)
                    successful += 1
                
                errors.extend(result.errors)
                warnings.extend(result.warnings)
                
            except Exception as e:
                failed += 1
                errors.append(f"Failed to extract release notes from {url}: {str(e)}")
        
        # Salvar documentos
        if save_to_repository and documents:
            try:
                await self.repository.save_many(documents)
            except Exception as e:
                errors.append(f"Failed to save release notes: {str(e)}")
        
        finished_at = datetime.now()
        
        return ScrapingResult(
            documents=tuple(documents),
            total_documents=len(documents),
            successful_scrapes=successful,
            failed_scrapes=failed,
            skipped_urls=0,
            started_at=started_at,
            finished_at=finished_at,
            source_urls=tuple(release_notes_urls),
            errors=tuple(errors),
            warnings=tuple(warnings),
        )
    
    async def get_versions_by_module(
        self,
        module: str,
    ) -> Dict[str, List[Document]]:
        """
        Recupera release notes organizadas por versão para um módulo.
        
        Args:
            module: Nome do módulo
        
        Returns:
            Dict[str, List[Document]]: Mapa versão -> documentos
        """
        # Buscar todos os release notes do módulo
        all_docs = await self.repository.find_by_module(module)
        
        # Filtrar release notes
        release_notes = [
            doc for doc in all_docs
            if doc.doc_type == DocumentType.RELEASE_NOTE
        ]
        
        # Agrupar por versão
        by_version: Dict[str, List[Document]] = {}
        for doc in release_notes:
            version = doc.metadata.get("version", "unknown")
            if version not in by_version:
                by_version[version] = []
            by_version[version].append(doc)
        
        return by_version
    
    async def get_latest_version(self, module: str) -> Optional[str]:
        """
        Retorna a versão mais recente de um módulo.
        
        Args:
            module: Nome do módulo
        
        Returns:
            Optional[str]: Versão mais recente ou None
        """
        versions_map = await self.get_versions_by_module(module)
        
        if not versions_map:
            return None
        
        # Ordenar versões (assumindo formato semver)
        versions = list(versions_map.keys())
        versions.sort(key=lambda v: self._parse_version(v), reverse=True)
        
        return versions[0] if versions else None
    
    async def compare_versions(
        self,
        module: str,
        version1: str,
        version2: str,
    ) -> Dict[str, Any]:
        """
        Compara duas versões de um módulo.
        
        Args:
            module: Nome do módulo
            version1: Primeira versão
            version2: Segunda versão
        
        Returns:
            Dict: Comparação entre versões
        """
        versions_map = await self.get_versions_by_module(module)
        
        docs_v1 = versions_map.get(version1, [])
        docs_v2 = versions_map.get(version2, [])
        
        return {
            "module": module,
            "version1": {
                "version": version1,
                "documents": len(docs_v1),
                "total_chars": sum(doc.char_count() for doc in docs_v1),
            },
            "version2": {
                "version": version2,
                "documents": len(docs_v2),
                "total_chars": sum(doc.char_count() for doc in docs_v2),
            },
        }
    
    def _enrich_release_note(self, doc: Document) -> Document:
        """
        Enriquece metadados de release note.
        
        Extrai informações como:
        - Versão (do título ou URL)
        - Data de release (se disponível)
        - Tipo de mudança (feature, bugfix, etc.)
        """
        # Extrair versão do título
        version = self._extract_version_from_title(doc.title)
        if version:
            doc.metadata["version"] = version
        
        # Extrair tipo de mudança do conteúdo
        change_types = self._extract_change_types(doc.content)
        if change_types:
            doc.metadata["change_types"] = change_types
        
        # Marcar como release note
        doc.metadata["is_release_note"] = True
        
        return doc
    
    def _extract_version_from_title(self, title: str) -> Optional[str]:
        """Extrai versão do título (ex: "Versão 6.10.4" -> "6.10.4")"""
        import re
        # Pattern para versões semver ou similar
        match = re.search(r'(\d+\.\d+\.\d+)', title)
        if match:
            return match.group(1)
        return None
    
    def _extract_change_types(self, content: str) -> List[str]:
        """Detecta tipos de mudança no conteúdo"""
        change_types = []
        content_lower = content.lower()
        
        keywords_map = {
            "feature": ["nova funcionalidade", "novo recurso", "feature"],
            "bugfix": ["correção", "corrigido", "bug fix", "fix"],
            "improvement": ["melhoria", "aprimoramento", "otimização"],
            "breaking": ["breaking change", "mudança incompatível"],
            "security": ["segurança", "security", "vulnerabilidade"],
        }
        
        for change_type, keywords in keywords_map.items():
            if any(kw in content_lower for kw in keywords):
                change_types.append(change_type)
        
        return change_types
    
    def _parse_version(self, version: str) -> tuple:
        """Parse versão para tuple (major, minor, patch) para ordenação"""
        try:
            parts = version.split(".")
            return tuple(int(p) for p in parts[:3])
        except:
            return (0, 0, 0)
    
    async def close(self) -> None:
        """Fecha recursos"""
        await self.scraper.close()
