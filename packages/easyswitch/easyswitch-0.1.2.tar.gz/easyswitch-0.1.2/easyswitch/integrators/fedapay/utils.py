"""
Utility module for mapping FedaPay currency IDs to ISO codes.
"""


class FedapayCurrencyMapper:
    """
    A utility class to map FedaPay currency IDs to their corresponding ISO codes.
    This class provides a method to retrieve the ISO code for a given FedaPay currency ID.
    It also allows for dynamic addition of new currency mappings.
    """
       
    _id_to_iso = {
        1: "XOF",  # Franc CFA BCEAO
        2: "GNF",  # Franc guinéen
        3: "EUR",  # Euro
    }

    @classmethod
    def get_iso(cls, currency_id: int) -> str:
        """
        Get the ISO code for a given FedaPay currency ID.
        Args:
            currency_id (int): The FedaPay currency ID.
        Returns:
            str: The ISO code corresponding to the currency ID.
        Raises:
            ValueError: If the currency ID is not recognized.
        """
        
        iso = cls._id_to_iso.get(currency_id)
        if not iso:
            raise ValueError(f"Unknown FedaPay currency_id: {currency_id}")
        return iso

    @classmethod
    def add_currency(cls, currency_id: int, iso: str):
        """        
        Add a new currency mapping to the mapper.
        Args:
            currency_id (int): The FedaPay currency ID.
            iso (str): The ISO code for the currency.
        """
        cls._id_to_iso[currency_id] = iso


if __name__ == "__main__":
    print(FedapayCurrencyMapper.get_iso(1))