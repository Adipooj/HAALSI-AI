def get_domain_columns(domain_varlists, domain, wave):
    return domain_varlists.get(domain, {}).get(wave, [])