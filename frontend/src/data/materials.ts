export type MaterialData = {
  key: string
  label: string
  include?: string
  sml: number | string
  density: number | string
  bulk_modulus: number | string
  shear_modulus: number | string
  eos_type?: number | string
  eosOptions?: { value: number | string; label: string; include?: string; type?: number | string }[]
  eosDefaults?: { [eosValue: string]: { [param: string]: number | string } }
}

const MATERIALS: MaterialData[] = [
  {
    key: 'basalt',
    label: 'Basalt',
    include: 'material_data/basalt.till.cfg',
    sml: 1.0,
    density: 2700,
    bulk_modulus: 26.7e9,
    shear_modulus: 22.7e9,
    eos_type: 5,
    eosOptions: [
      { value: 5, label: 'Tillotson', include: 'material_data/basalt.till.cfg', type: 5 },
      { value: 1, label: 'Murnaghan', include: 'material_data/basalt.murn.cfg', type: 1 },
    ],
    // per-eos default parameters (keys match EOS field keys without the `eos.` prefix)
    eosDefaults: {
      '5': {
        till_rho_0: 2700,
        till_A: 1e11,
        till_B: 1e11,
        till_E_0: 1e5,
        till_a: 0.5,
        till_b: 0.5,
      },
      '1': {
        rho_0: 2700,
        bulk_modulus: 26.7e9,
        n: 1.0,
        rho_limit: 0.9,
      },
    },
  },
  {
    key: 'aluminum',
    label: 'Aluminium',
    include: 'material_data/aluminum.till.cfg',
    sml: 1.0,
    density: 2700,
    bulk_modulus: 52.27e9,
    shear_modulus: 26.9e9,
    eos_type: 2,
    eosOptions: [
      { value: 2, label: 'ANEOS', include: 'material_data/aluminum.till.cfg', type: 2 },
      { value: 1, label: 'Murnaghan', include: 'material_data/aluminum.murn.cfg', type: 1 },
    ],
    eosDefaults: {
      '2': {
        till_rho_0: 2700,
        till_A: 8e10,
        till_B: 8e10,
        till_E_0: 1e5,
        till_a: 0.5,
        till_b: 0.5,
      },
      '1': {
        rho_0: 2700,
        bulk_modulus: 52.27e9,
        n: 1.0,
        rho_limit: 0.9,
      },
    },
  },
  {
    key: 'water',
    label: 'Water',
    include: '',
    sml: 1.0,
    density: 1000,
    bulk_modulus: 2.2e9,
    shear_modulus: 0,
    eos_type: 5,
    eosOptions: [{ value: 5, label: 'Tillotson', include: '', type: 5 }, { value: 0, label: 'Custom', include: '', type: 0 }],
    eosDefaults: {
      '5': {
        till_rho_0: 1.0e3,
        till_A: 2.0e10,
        till_B: 1.0e10,
        till_E_0: 2.0e6,
        till_a: 0.5,
        till_b: 0.9,
        rho_limit: 0.95,
        cs_limit: 40.0,
      },
    },
  },
  {
    key: 'iron',
    label: 'Iron',
    include: '',
    sml: 1.0,
    density: 7874,
    bulk_modulus: 1.6e11,
    shear_modulus: 7.9e10,
    eos_type: 5,
    eosOptions: [{ value: 5, label: 'Tillotson', include: '', type: 5 }, { value: 0, label: 'Custom', include: '', type: 0 }],
    eosDefaults: {
      '5': {
        till_rho_0: 7.8e3,
        till_A: 128.0e9,
        till_B: 105.0e9,
        till_E_0: 9.5e6,
        till_a: 0.5,
        till_b: 1.5,
        rho_limit: 0.9,
        cs_limit: 40.0,
      },
    },
  },
  {
    key: 'granite',
    label: 'Granite',
    include: '',
    sml: 1.0,
    density: 2600,
    bulk_modulus: 5.0e10,
    shear_modulus: 2.6e10,
    eos_type: 5,
    eosOptions: [{ value: 5, label: 'Tillotson', include: '', type: 5 }, { value: 0, label: 'Custom', include: '', type: 0 }],
    eosDefaults: {
      '5': {
        till_rho_0: 2.68e3,
        till_A: 1.8e10,
        till_B: 1.8e10,
        till_E_0: 1.6e7,
        till_a: 0.5,
        till_b: 1.3,
        rho_limit: 0.9,
        cs_limit: 30.0,
      },
    },
  },
  {
    key: 'ice',
    label: 'Ice',
    include: '',
    sml: 1.0,
    density: 917,
    bulk_modulus: 9.0e9,
    shear_modulus: 3.5e9,
    eos_type: 5,
    eosOptions: [{ value: 5, label: 'Tillotson', include: '', type: 5 }, { value: 0, label: 'Custom', include: '', type: 0 }],
    eosDefaults: {
      '5': {
        till_rho_0: 0.917e3,
        till_A: 9.47e9,
        till_B: 9.47e9,
        till_E_0: 10.0e6,
        till_a: 0.3,
        till_b: 0.1,
        rho_limit: 0.9,
        cs_limit: 30.0,
      },
    },
  },
  { key: 'custom', label: 'Custom', include: '', sml: 1.0, density: 1000, bulk_modulus: 1.0e10, shear_modulus: 0, eos_type: 0, eosOptions: [{ value: 0, label: 'Custom', include: '', type: 0 }] },
]

export default MATERIALS

export function getMaterialByKey(key: string): MaterialData {
  return (MATERIALS.find((m) => m.key === key) || MATERIALS.find((m) => m.key === 'custom')) as MaterialData
}
