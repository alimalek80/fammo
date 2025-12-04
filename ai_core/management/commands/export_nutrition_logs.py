"""
Django management command to export nutrition prediction logs for training data.

Usage:
    python manage.py export_nutrition_logs
    python manage.py export_nutrition_logs --format=csv --output=/tmp/logs.csv
    python manage.py export_nutrition_logs --species=dog --health-goal=weight_loss
"""

import csv
import json
import os
from django.core.management.base import BaseCommand, CommandError
from ai_core.models import NutritionPredictionLog


class Command(BaseCommand):
    help = 'Export nutrition prediction logs to JSONL or CSV for training data analysis'

    def add_arguments(self, parser):
        """Define command-line arguments."""
        parser.add_argument(
            '--format',
            type=str,
            choices=['jsonl', 'csv'],
            default='jsonl',
            help='Output format: jsonl (default) or csv'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='Output file path (default: nutrition_logs.jsonl or nutrition_logs.csv in current directory)'
        )
        
        parser.add_argument(
            '--species',
            type=str,
            default=None,
            help='Filter by species (e.g., dog, cat)'
        )
        
        parser.add_argument(
            '--health-goal',
            type=str,
            default=None,
            help='Filter by health goal (e.g., weight_loss, maintenance)'
        )

    def handle(self, *args, **options):
        """Execute the export command."""
        # Parse options
        output_format = options['format']
        output_path = options['output']
        species_filter = options['species']
        health_goal_filter = options['health_goal']
        
        # Determine output filename if not provided
        if not output_path:
            output_path = f'nutrition_logs.{output_format}'
        
        # Build queryset with filters
        queryset = NutritionPredictionLog.objects.all().order_by('id')
        
        filters_applied = []
        if species_filter:
            queryset = queryset.filter(species=species_filter)
            filters_applied.append(f"species={species_filter}")
        
        if health_goal_filter:
            queryset = queryset.filter(health_goal=health_goal_filter)
            filters_applied.append(f"health_goal={health_goal_filter}")
        
        # Get total count
        total_count = queryset.count()
        
        # Export based on format
        if output_format == 'jsonl':
            self._export_jsonl(queryset, output_path)
        else:
            self._export_csv(queryset, output_path)
        
        # Print summary
        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully exported {total_count} row(s)'))
        self.stdout.write(self.style.SUCCESS(f'✓ Output file: {os.path.abspath(output_path)}'))
        
        if filters_applied:
            self.stdout.write(self.style.WARNING(f'ℹ Filters applied: {", ".join(filters_applied)}'))
        
        if total_count == 0:
            self.stdout.write(self.style.WARNING('⚠ No rows matched the filters'))

    def _export_jsonl(self, queryset, output_path):
        """
        Export queryset to JSONL format (one JSON object per line).
        
        Args:
            queryset: Django queryset of NutritionPredictionLog
            output_path: Path to output file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for log in queryset.iterator(chunk_size=100):
                row = {
                    'id': log.id,
                    'created_at': log.created_at.isoformat(),
                    'source': log.source,
                    'backend': log.backend,
                    'model_version': log.model_version,
                    'species': log.species,
                    'life_stage': log.life_stage,
                    'breed_size_category': log.breed_size_category,
                    'health_goal': log.health_goal,
                    'weight_kg': log.weight_kg,
                    'age_years': log.age_years,
                    'body_condition_score': log.body_condition_score,
                    'input': log.input_payload,
                    'output': log.output_payload,
                }
                
                # Write one JSON object per line
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
    
    def _export_csv(self, queryset, output_path):
        """
        Export queryset to CSV format.
        
        Args:
            queryset: Django queryset of NutritionPredictionLog
            output_path: Path to output file
        """
        # Define CSV columns
        fieldnames = [
            'id',
            'created_at',
            'source',
            'backend',
            'model_version',
            'species',
            'life_stage',
            'breed_size_category',
            'health_goal',
            'weight_kg',
            'age_years',
            'body_condition_score',
            'input_payload',
            'output_payload',
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data rows
            for log in queryset.iterator(chunk_size=100):
                row = {
                    'id': log.id,
                    'created_at': log.created_at.isoformat(),
                    'source': log.source,
                    'backend': log.backend,
                    'model_version': log.model_version,
                    'species': log.species,
                    'life_stage': log.life_stage,
                    'breed_size_category': log.breed_size_category,
                    'health_goal': log.health_goal,
                    'weight_kg': log.weight_kg,
                    'age_years': log.age_years,
                    'body_condition_score': log.body_condition_score,
                    'input_payload': json.dumps(log.input_payload, ensure_ascii=False),
                    'output_payload': json.dumps(log.output_payload, ensure_ascii=False),
                }
                
                writer.writerow(row)
