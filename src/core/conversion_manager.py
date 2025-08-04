#!/usr/bin/env python3
"""
Module pour gérer les conversions de fichiers
"""

import os
import subprocess
from core.config import FILE_FORMATS
from core.metadata_manager import MetadataManager


class ConversionManager:
    """Gestionnaire des conversions de fichiers"""
    
    @staticmethod
    def build_command(file_path, tool_type, options):
        """
        Construit la commande de conversion
        
        Args:
            file_path: Chemin du fichier à convertir
            tool_type: Type d'outil ('epub', 'cbr', 'cbz')
            options: Dictionnaire des options
            
        Returns:
            list: Commande à exécuter
        """
        if tool_type not in FILE_FORMATS:
            return None
            
        script_name = FILE_FORMATS[tool_type]['script']
        cmd = [f"./{script_name}"]
        
        # Ajout des options
        if options.get('output_dir'):
            cmd.extend(["--output-dir", options['output_dir']])
            
        if options.get('recursive'):
            cmd.append("--recursive")
            
        if options.get('force'):
            cmd.append("--force")
            
        if options.get('grayscale'):
            cmd.append("--grayscale")
            
        resize = options.get('resize')
        if resize:
            cmd.extend(["--resize", resize])
            
        if options.get('zip_output'):
            cmd.append("--zip-output")
            
        if options.get('clean_tmp'):
            cmd.append("--clean-tmp")
            
        if options.get('open_output'):
            cmd.append("--open-output-dir")
            
        if options.get('verbose'):
            cmd.append("--verbose")
            
        # Ajout du fichier à convertir
        cmd.append(file_path)
        
        return cmd
    
    @staticmethod
    def process_metadata(pdf_path, tool_type, options, index=None):
        """
        Traite les métadonnées PDF après conversion
        Args:
            pdf_path: Chemin du fichier PDF
            tool_type: Type d'outil
            options: Options de conversion
            index: Numéro d'incrémentation (pour le titre)
        Returns:
            str: Chemin du fichier final (renommé si nécessaire)
        """
        if not options.get('edit_metadata') and not options.get('auto_rename'):
            return pdf_path
        try:
            format_type = 'manga' if tool_type in ['cbr', 'cbz'] else 'epub'
            filename = os.path.basename(pdf_path)
            info = MetadataManager.extract_title_info(filename, format_type)
            if options.get('edit_metadata'):
                MetadataManager.edit_pdf_metadata(pdf_path, info, format_type, options, index)
                print(f"📊 Metadata updated for: {filename}")
            if options.get('auto_rename'):
                new_path = MetadataManager.rename_file_with_metadata(pdf_path, format_type, options, index)
                if new_path and new_path != pdf_path:
                    print(f"🏷️ Renamed: {filename} → {os.path.basename(new_path)}")
                    return new_path
            return pdf_path
        except Exception as e:
            print(f"❌ Error processing metadata: {e}")
            return pdf_path

    @staticmethod
    def convert_single_file(file_path, tool_type, options, index=None):
        """
        Convertit un seul fichier
        Args:
            file_path: Chemin du fichier
            tool_type: Type d'outil
            options: Options de conversion
            index: Numéro d'incrémentation (pour le titre)
        Returns:
            bool: True si succès, False sinon
        """
        try:
            cmd = ConversionManager.build_command(file_path, tool_type, options)
            if not cmd:
                return False
            process = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=os.getcwd()
            )
            if process.returncode == 0:
                output_dir = options.get('output_dir', './pdfs')
                filename = os.path.basename(file_path)
                pdf_name = os.path.splitext(filename)[0] + '.pdf'
                pdf_path = os.path.join(output_dir, pdf_name)
                if os.path.exists(pdf_path):
                    ConversionManager.process_metadata(pdf_path, tool_type, options, index)
                return True
            else:
                return False
        except Exception:
            return False
    
    @staticmethod
    def run_sequential_conversion(files_to_convert, options, callback=None):
        """
        Exécute les conversions de manière séquentielle
        
        Args:
            files_to_convert: Liste des fichiers à convertir
            options: Options de conversion
            callback: Fonction de callback pour le progrès
            
        Returns:
            tuple: (succès, échecs)
        """
        completed = 0
        failed = 0
        
        for file_path, tool_type in files_to_convert:
            try:
                if callback:
                    callback(f"Converting: {os.path.basename(file_path)} ({tool_type.upper()})")
                    
                success = ConversionManager.convert_single_file(file_path, tool_type, options)
                
                if success:
                    completed += 1
                    if callback:
                        callback(f"✅ Successfully converted: {os.path.basename(file_path)}")
                else:
                    failed += 1
                    if callback:
                        callback(f"❌ Failed to convert: {os.path.basename(file_path)}")
                        
            except Exception as e:
                failed += 1
                if callback:
                    callback(f"❌ Error converting {os.path.basename(file_path)}: {e}")
                    
        return completed, failed
    
    @staticmethod
    def run_parallel_conversion(files_to_convert, options, max_workers, callback=None):
        """
        Exécute les conversions en parallèle
        
        Args:
            files_to_convert: Liste des fichiers à convertir
            options: Options de conversion
            max_workers: Nombre maximum de workers
            callback: Fonction de callback pour le progrès
            
        Returns:
            tuple: (succès, échecs)
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        completed = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Soumettre toutes les tâches
            future_to_file = {}
            for file_path, tool_type in files_to_convert:
                future = executor.submit(
                    ConversionManager.convert_single_file, 
                    file_path, 
                    tool_type, 
                    options
                )
                future_to_file[future] = (file_path, tool_type)
                
            # Traiter les tâches terminées
            for future in as_completed(future_to_file):
                file_path, tool_type = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        completed += 1
                        if callback:
                            callback(f"✅ Successfully converted: {os.path.basename(file_path)}")
                    else:
                        failed += 1
                        if callback:
                            callback(f"❌ Failed to convert: {os.path.basename(file_path)}")
                except Exception as e:
                    failed += 1
                    if callback:
                        callback(f"❌ Error converting {os.path.basename(file_path)}: {e}")
                        
        return completed, failed 