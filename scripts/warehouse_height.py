"""Approved revision: warehouse ridge datum 12m above finished floor."""
def apply_warehouse_height(scene):
    floor = .22
    rise = 11.5 * .249328
    ridge = floor + 12
    eave = ridge - rise
    delta = eave - 6.2
    roof_names = {'Talang memanjang', 'Sambungan atap', 'Gording CNP125',
                  'Nok atap', 'Rafter WF250', 'Haunch rafter', 'Ikatan angin silang',
                  'Highbay housing', 'Highbay diffuser'}
    for e in scene['elements']:
        n = e['name']
        if n == 'Kolom WF250' and e['a'][0] != 3:
            e['b'][2] += delta
        elif e['kind'] == 'box' and (n.startswith(('Fasad Gudang', 'Belakang Gudang')) or n == 'Dinding pemisah'):
            # Extend only wall pieces ending at the original eave. Doors/windows stay fixed.
            if abs(e['p'][2] + e['s'][2] - 6.2) < 1e-6:
                e['s'][2] += delta
        elif n == 'Pipa air hujan':
            e['h'] += delta
        elif n in roof_names or n.startswith(('Penutup atap Gudang', 'Dinding segitiga Gudang')):
            for key in ('p', 'a', 'b'):
                if key in e: e[key][2] += delta
            for p in e.get('points', []): p[2] += delta
    for p in scene['lights']:
        if abs(p[2] - 5.56) < 1e-6: p[2] += delta
    scene['revision'] = 4
    scene['warehouse_height'] = dict(finished_floor=floor, ridge_datum=ridge,
                                    eave_datum=eave, ridge_above_floor=12,
                                    eave_above_floor=eave-floor, roof_rise=rise)
    scene['avatar_height_m'] = 1.70
    scene['assumptions'] = [a for a in scene['assumptions'] if not a.startswith('Warehouse finished floor')]
    scene['assumptions'].append('Revision 04 approved B: warehouse ridge datum 12.00m above finished floor +0.22m; eave 9.132728m above floor. Roof pitch and footprints retained. Ridge cap/cover thickness sits above the roof datum. Columns, upper walls, roof framing, rainpipes and highbay lights follow the height change; windows, access doors, canopies and western shed retain their elevations. Member sizes remain illustrative and require structural redesign for construction.')
    scene['assumptions'].append('Walkthrough block character is 1.70m from boot soles to helmet top in standing pose. Eye and follow-camera heights scale with the character; collision height adds a 20mm clearance allowance.')
    return scene
