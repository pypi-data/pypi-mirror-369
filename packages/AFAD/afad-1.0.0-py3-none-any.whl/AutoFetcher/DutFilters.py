from packaging import version
import re


class DutFilters:
    __testing_env = False

    def __init__(self):
        pass

    @staticmethod
    def enable_test(enable: bool = True):
        DutFilters.__testing_env = enable

    @staticmethod
    def __print(message: str = ""):
        if DutFilters.__testing_env:
            print(message)

    @staticmethod
    def __normalize_version(v: str):
        """Converts version like 4.32.1F to 4.32.1.post1 for comparison."""
        if '-' in v:
            base_version = v.split('-', 1)[0]
            DutFilters.__print(f"[normalize_version] EOS Version contains '-' so, Base Version : {base_version}")
            normalized_base = DutFilters.__normalize_version(base_version)
            # For versions with '-', we only normalize the part before it.
            # We can return the normalized base along with the rest of the string if needed.
            # For now, let's just normalize the base.
            return normalized_base
        else:
            match = re.match(r'(\d+\.\d+\.\d+)([FM]?\+?)?', v)
            if not match:
                return v
            base, suffix = match.groups()
            DutFilters.__print(f"[normalize_version] Separating base and suffix, Base : {base} suffix : {suffix}")
            suffix = suffix or ''
            suffix_map = {'F': '.post1', 'M': '.post2', 'F+': '.post3', 'M+': '.post4'}
            return base + suffix_map.get(suffix, '')

    @staticmethod
    def is_valid_eos_version(allowed_ranges: dict[str, tuple[str, str]], v: str):
        """Check if EOS version is within the allowed range."""
        try:
            for major, (low, high) in allowed_ranges.items():
                if v.startswith(major):
                    v_norm = DutFilters.__normalize_version(v)
                    low_norm = DutFilters.__normalize_version(low)
                    high_norm = DutFilters.__normalize_version(high)
                    DutFilters.__print(f"[normalize_version] v_norm : {v_norm} low_norm : {low_norm} and high_norm : {high_norm}")
                    if version.parse(low_norm) <= version.parse(v_norm) <= version.parse(high_norm):
                        return True
        except Exception as e:
            print(f"Error while parsing version '{v}': {e}")
        return False

    @staticmethod
    def has_substr(pattern: str, main_str: str):
        return re.search(pattern, main_str)
