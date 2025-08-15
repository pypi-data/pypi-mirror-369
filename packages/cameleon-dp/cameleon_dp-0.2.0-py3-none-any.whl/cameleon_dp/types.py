from dataclasses import dataclass

@dataclass
class Block:
    j_lo: int
    j_hi: int
    i_lo: int
    i_hi: int
    block_id: int = 0
    depth: int = 0
    orientation: str = "root"  # 'i' or 'j' or 'root'
