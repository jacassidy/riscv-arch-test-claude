## Coverage caveats worth documenting in .svh


When coverpoint conceptually unimplementable (e.g. observing FS state-transition on hardware allowed to be always-Dirty, or crossing on misa.V when misa permitted to be all-zero read-only), drop unimplementable cross from .svh and add comment explaining why — but keep test exercising scenario. Cross-model signature comparison still catches divergence.
