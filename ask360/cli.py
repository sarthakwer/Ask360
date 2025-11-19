"""CLI interface for Ask360."""

import sys
from ask360.ask360_core import answer


def main():
    """Main CLI entry point."""
    if len(sys.argv) > 1:
        # Question provided as argument
        question = ' '.join(sys.argv[1:])
        result = answer(question)
        _print_result(result)
    else:
        # Interactive mode
        print("Ask360 - FreshFoods Yogurt Insights")
        print("Type 'exit' or 'quit' to exit.\n")
        
        while True:
            try:
                question = input("Ask360> ").strip()
                if not question:
                    continue
                if question.lower() in ('exit', 'quit'):
                    break
                
                result = answer(question)
                _print_result(result)
                print()  # Blank line between Q&A
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")


def _print_result(result: dict):
    """Print formatted result to console."""
    print(f"\nIntent: {result['intent']}")
    
    # Metadata
    if result.get('metadata'):
        metadata = result['metadata']
        print("\n📊 Query Metadata:")
        if metadata.get('data_sources'):
            print("  Data Sources:")
            for source in metadata['data_sources']:
                print(f"    • {source}")
        if metadata.get('time_range'):
            print(f"  Time Range: {metadata['time_range']}")
        if metadata.get('regions'):
            print("  Regions:")
            for region in metadata['regions']:
                print(f"    • {region}")
        if metadata.get('filters'):
            print("  Filters:")
            for filter_item in metadata['filters']:
                print(f"    • {filter_item}")
    
    if result.get('kpis'):
        print("\nKPIs:")
        for kpi in result['kpis']:
            print(f"  {kpi['label']}: {kpi['value']}")
    
    if result.get('text'):
        print("\nSummary:")
        for line in result['text']:
            print(f"  {line}")
    
    if result.get('table'):
        print("\nTable:")
        # Simple table display
        if result['table']:
            keys = result['table'][0].keys()
            print("  " + " | ".join(keys))
            print("  " + "-" * 50)
            for row in result['table'][:10]:  # Limit to 10 rows
                print("  " + " | ".join(str(row.get(k, '')) for k in keys))
    
    if result.get('chart_path'):
        print(f"\nChart saved to: {result['chart_path']}")


if __name__ == '__main__':
    main()

