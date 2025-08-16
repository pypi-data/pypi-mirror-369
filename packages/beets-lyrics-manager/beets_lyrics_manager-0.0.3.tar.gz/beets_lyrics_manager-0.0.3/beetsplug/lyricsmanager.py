#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
beets plugin for managing lyrics files (.lrc) alongside music files.

This plugin:
1. During import: finds and copies .lrc files with the same name as music files
2. During move: moves .lrc files along with their corresponding music files
3. Renames .lrc files to match the new music file names
"""

import os
import shutil
from pathlib import Path
from beets.plugins import BeetsPlugin
from beets.util import displayable_path, syspath, bytestring_path
from beets import config


class LyricsManagerPlugin(BeetsPlugin):
    """Plugin for managing lyrics files alongside music files."""

    def __init__(self):
        super().__init__()
        # Register event listeners
        self.register_listener('item_imported', self.on_item_imported)
        self.register_listener('item_moved', self.on_item_moved)
        self.register_listener('item_copied', self.on_item_copied)
        self.register_listener('item_linked', self.on_item_linked)
        self.register_listener('item_hardlinked', self.on_item_hardlinked)
        self.register_listener('item_reflinked', self.on_item_reflinked)
        
        # Configuration
        self.lyrics_extensions = self.config['extensions'].get()
        self.copy_lyrics = self.config['copy_lyrics'].get(True)
        self.move_lyrics = self.config['move_lyrics'].get(True)
        
        self._log.debug(
            'LyricsManager plugin loaded, extensions: {0}, copy lyrics: {1}, move lyrics: {2}',
            self.lyrics_extensions, self.copy_lyrics, self.move_lyrics
        )

    def find_lyrics_file(self, music_path):
        """Find lyrics file with the same name as the music file."""
        music_path = Path(syspath(music_path))
        music_dir = music_path.parent
        music_stem = music_path.stem
        
        for ext in self.lyrics_extensions:
            lyrics_path = music_dir / f"{music_stem}{ext}"
            if lyrics_path.exists():
                return lyrics_path
        return None

    def get_lyrics_destination(self, music_path, lyrics_path):
        """Get the destination path for lyrics file based on music file path."""
        music_path = Path(syspath(music_path))
        lyrics_path = Path(syspath(lyrics_path))
        
        # Use the same directory as music file, same stem, but keep lyrics extension
        return music_path.parent / f"{music_path.stem}{lyrics_path.suffix}"

    def _handle_lyrics_operation(self, source_path, destination_path, operation_type, operation_func):
        """
        Generic handler for lyrics file operations.
        
        Args:
            source_path: Source music file path
            destination_path: Destination music file path  
            operation_type: Type of operation ('copy', 'move', 'link')
            operation_func: Function to perform the operation (copy2, move, etc.)
        """
        lyrics_source = self.find_lyrics_file(source_path)
        if not lyrics_source:
            return
            
        lyrics_dest = self.get_lyrics_destination(destination_path, lyrics_source)
        
        # Skip if source and destination are the same
        if lyrics_dest == lyrics_source:
            self._log.debug('Lyrics file already in correct location: {0}', 
                          displayable_path(lyrics_source))
            return
            
        try:
            # Create destination directory if it doesn't exist
            lyrics_dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Perform the operation
            operation_func(syspath(lyrics_source), syspath(lyrics_dest))
            
            self._log.info('{0} lyrics file: {1} -> {2}', 
                         operation_type.title(),
                         displayable_path(lyrics_source), 
                         displayable_path(lyrics_dest))
                         
        except (OSError, IOError) as e:
            self._log.error('Failed to {0} lyrics file {1}: {2}', 
                          operation_type,
                          displayable_path(lyrics_source), e)

    def on_item_imported(self, lib, item):
        """Handle item import - copy lyrics file if found."""
        if not self.copy_lyrics:
            return
            
        self._handle_lyrics_operation(
            item.path, item.path, 'copy', shutil.copy2
        )



    def on_item_moved(self, item, source, destination):
        """Move lyrics file along with the music file."""
        if not self.move_lyrics:
            return
            
        self._handle_lyrics_operation(
            source, destination, 'move', shutil.move
        )

    def on_item_copied(self, item, source, destination):
        """Copy lyrics file when music file is copied."""
        if not self.copy_lyrics:
            return
            
        self._handle_lyrics_operation(
            source, destination, 'copy', shutil.copy2
        )

    def on_item_linked(self, item, source, destination):
        """Handle lyrics file when music file is linked."""
        if not self.copy_lyrics:
            return
            
        self._handle_lyrics_operation(
            source, destination, 'copy', shutil.copy2
        )

    def on_item_hardlinked(self, item, source, destination):
        """Handle lyrics file when music file is hardlinked."""
        if not self.copy_lyrics:
            return
            
        self._handle_lyrics_operation(
            source, destination, 'copy', shutil.copy2
        )

    def on_item_reflinked(self, item, source, destination):
        """Handle lyrics file when music file is reflinked."""
        if not self.copy_lyrics:
            return
            
        self._handle_lyrics_operation(
            source, destination, 'copy', shutil.copy2
        ) 