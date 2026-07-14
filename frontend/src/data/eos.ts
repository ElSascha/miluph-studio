export type EosField = { key: string; label: string; default?: string }

export type EosDef = {
  value: number | string
  label: string
  include?: string
  type?: number | string
  fields: EosField[]
}

const EOS_DEFS: EosDef[] = [
  {
    value: 1,
    label: 'Murnaghan',
    include: '',
    type: 1,
    fields: [
      { key: 'eos.rho_0', label: 'Reference density (rho_0)', default: '0' },
      { key: 'eos.bulk_modulus', label: 'Bulk modulus', default: '0' },
      { key: 'eos.n', label: 'n (exponent)', default: '1' },
      { key: 'eos.rho_limit', label: 'rho_limit', default: '0.9' },
    ],
  },
  {
    value: 2,
    label: 'Tillotson',
    include: '',
    type: 2,
    fields: [
      { key: 'eos.till_rho_0', label: 'Tillotson rho_0' },
      { key: 'eos.till_A', label: 'Tillotson A' },
      { key: 'eos.till_B', label: 'Tillotson B' },
      { key: 'eos.till_E_0', label: 'Tillotson E_0' },
      { key: 'eos.till_a', label: 'Tillotson a' },
      { key: 'eos.till_b', label: 'Tillotson b' },
    ],
  },
  {
    value: 13,
    label: 'ANEOS',
    include: '',
    type: 13,
    fields: [{ key: 'eos.aneos_param', label: 'ANEOS param (example)' }],
  },
  { value: 0, label: 'Custom/Other', fields: [] },
]

export default EOS_DEFS

export function getEosByValue(v: number | string) {
  return EOS_DEFS.find((e) => String(e.value) === String(v)) || EOS_DEFS[0]
}
