@app.route('/api/menu-data', methods=['GET'])
def menu_data():
    """Get all menu data from CSV."""
    # Read menu items from CSV
    menu_items = read_menu_items_csv('data/menu_items.csv')

    # Read pricing rules from CSV
    pricing_rules = read_pricing_rules_csv('data/pricing_config.csv')

    # Organize items by category
    proteins = [item for item in menu_items if item['category'] == 'proteins']
    sauces = [item for item in menu_items if item['category'] == 'sauces']

    # Organize bases by type
    bases = {}
    for item in menu_items:
        if item['category'] == 'bases':
            base_type = json.loads(item['attributes'])['base_type']
            if base_type not in bases:
                bases[base_type] = []
            bases[base_type].append({
                'name': item['item'],
                'price': float(item['price']),
                'description': item['description']
            })

    # Get veggie items with premium flags
    veggies = []
    for item in menu_items:
        if item['category'] == 'veggies':
            attrs = json.loads(item['attributes'])
            veggies.append({
                'name': item['item'],
                'price': float(item['price']),
                'description': item['description'],
                'premium': attrs.get('premium', False)
            })

    return jsonify({
        'success': True,
        'menu_data': {
            'proteins': proteins,
            'sauces': sauces,
            'bases': bases,
            'veggies': veggies
        },
        'pricing_rules': pricing_rules
    })