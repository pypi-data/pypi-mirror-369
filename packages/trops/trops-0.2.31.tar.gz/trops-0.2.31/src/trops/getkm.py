import os
import tempfile
from configparser import ConfigParser
from textwrap import dedent

from .trops import TropsMain


class TropsGetKm:
    def __init__(self, args, other_args):
        self.args = args
        self.other_args = other_args

        if other_args:
            msg = f"""\
                Unsupported argments: {', '.join(other_args)}
                > trops getkm --help"""
            print(dedent(msg))
            exit(1)

        # Validate flags
        all_flag = getattr(args, 'all', False)
        env_flag = getattr(args, 'env', None)
        if (not all_flag and not env_flag) or (all_flag and env_flag):
            print('ERROR: specify exactly one of -a/--all or -e/--env <env>')
            exit(1)

        # Validate target path presence (existence is checked later)
        if not hasattr(args, 'path') or not args.path:
            print('ERROR: target <path> is required')
            exit(1)

        # Load config from $TROPS_DIR/trops.cfg
        trops_dir = os.getenv('TROPS_DIR')
        if not trops_dir:
            print('ERROR: TROPS_DIR is not set')
            exit(1)
        cfg_path = os.path.join(trops_dir, 'trops.cfg')
        if not os.path.isfile(cfg_path):
            print(f"ERROR: config not found: {cfg_path}")
            exit(1)

        self.config = ConfigParser()
        self.config.read(cfg_path)

        # Build list of environments to process
        if all_flag:
            self.envs = [s for s in self.config.sections()]
        else:
            if not self.config.has_section(env_flag):
                print(f"ERROR: env '{env_flag}' not found in config")
                exit(1)
            self.envs = [env_flag]

    def _git_for_env(self, env_name, args_list):
        # Build a TropsMain instance for the target env to get git_cmd preconfigured
        class _A:
            def __init__(self, env):
                self.env = env
                self.sudo = False
                self.verbose = False

        tm = TropsMain(_A(env_name), [])
        # Call git directly to avoid wrapper normalization of tokens like --prefix=<path>
        import subprocess as _subprocess
        result = _subprocess.run(tm.git_cmd + args_list)
        if result.returncode != 0:
            exit(result.returncode)

    def run(self):
        # Resolve and prepare output directory now; create it if it does not exist
        from .utils import absolute_path as _abs
        self.target_prefix = _abs(self.args.path)
        os.makedirs(self.target_prefix, exist_ok=True)

        # Create a temporary index path and ensure it does not exist on disk
        fd, tmp_index_path = tempfile.mkstemp(prefix='trops_idx_')
        try:
            os.close(fd)
        except Exception:
            pass
        try:
            if os.path.exists(tmp_index_path):
                os.unlink(tmp_index_path)
        except Exception:
            pass

        # Preserve original env
        orig_index = os.environ.get('GIT_INDEX_FILE')
        try:
            os.environ['GIT_INDEX_FILE'] = tmp_index_path
            for env_name in self.envs:
                # Pull km_dir from config for each env
                try:
                    km_dir = self.config[env_name]['km_dir']
                except KeyError:
                    print(f"WARNING: skipping env '{env_name}' due to missing km_dir")
                    continue

                # If km_dir begins with '/', remove only the first '/' for the git ref
                km_dir_ref = km_dir[1:] if km_dir.startswith('/') else km_dir

                # 1) read-tree (no prefix; will override work-tree on checkout)
                read_tree_args = [
                    'read-tree', f'origin/trops/{env_name}:{km_dir_ref}'
                ]
                self._git_for_env(env_name, read_tree_args)

                # 2) checkout-index -a with overridden work-tree to target output directory
                checkout_args = [f'--work-tree={self.target_prefix}', 'checkout-index', '-a']
                self._git_for_env(env_name, checkout_args)
        finally:
            # Cleanup env var and temp file
            if orig_index is None:
                os.environ.pop('GIT_INDEX_FILE', None)
            else:
                os.environ['GIT_INDEX_FILE'] = orig_index
            try:
                if os.path.exists(tmp_index_path):
                    os.unlink(tmp_index_path)
            except Exception:
                pass


def run(args, other_args):
    gk = TropsGetKm(args, other_args)
    gk.run()


def add_getkm_subparsers(subparsers):
    parser_getkm = subparsers.add_parser('getkm', help='extract km files to a target path using a temporary index')
    group = parser_getkm.add_mutually_exclusive_group(required=False)
    group.add_argument('-a', '--all', action='store_true', help='process all environments found in config')
    group.add_argument('-e', '--env', help='process a specific environment name')
    parser_getkm.add_argument('path', help='target directory path to extract files into (used as --prefix)')
    parser_getkm.set_defaults(handler=run)


