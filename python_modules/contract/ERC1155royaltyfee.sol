pragma solidity ^0.8.2;

import "./@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
//import "./@openzeppelin/contracts/interfaces/IERC2981.sol";
import "./@openzeppelin/contracts/token/common/ERC2981.sol";
import "./@openzeppelin/contracts/access/Ownable.sol";
import "./@openzeppelin/contracts/security/Pausable.sol";
import "./@openzeppelin/contracts/utils/Strings.sol";
import "./@openzeppelin/contracts/utils/ContextMixin.sol";

/// @custom:security-contact <security email address>
contract MyNFT is ERC1155, Ownable, Pausable, ContextMixin,ERC2981 {

    using Strings for uint256;
    string public name;
    string public symbol;
    address private _recipient;

    constructor(string memory _name, string memory _symbol) ERC1155("") {
        name = _name;
        symbol = _symbol;
        _recipient = owner();
    }

    function pause() public onlyOwner {
        _pause();
    }

    function unpause() public onlyOwner {
        _unpause();
    }
    function multisend (address from , address[] memory to, uint256[] memory tokenIds, uint256[] memory amount) public onlyOwner returns (uint256) {
        uint256 i = 0;
        while (i < to.length) {
        safeTransferFrom(from, to[i],tokenIds[i], amount[i], "");
           i += 1;
        }
        return(i);
    }
    function mint(string memory _uri, uint256 id,  uint256 _amount ) public returns (uint256) {
        _mint(msg.sender, id, _amount, "");
        _setURI(_uri);                  // uri(tokenId);
        return id;
    }

    function setroyalty_mint(string memory _uri, uint256 id,  uint256 _amount, address _receiver, uint96 _feeNumerator ) public returns (uint256) {
        _mint(msg.sender, id, _amount, "");
        _setURI(_uri);                  // uri(tokenId);
         setTokenRoyalty(id, _receiver, _feeNumerator);
        return id;
    }

    function mintBatch(address to, uint256[] memory ids, uint256[] memory amounts, bytes memory data)
        public
        onlyOwner
    {
        _mintBatch(to, ids, amounts, data);
    }

    function _beforeTokenTransfer(address operator, address from, address to, uint256[] memory ids, uint256[] memory amounts, bytes memory data)
        internal
        whenNotPaused
        override
    {
        super._beforeTokenTransfer(operator, from, to, ids, amounts, data);
    }

     function setDefaultRoyalty(address _receiver, uint96 _feeNumerator)
        public
        onlyOwner
    {
        _setDefaultRoyalty(_receiver, _feeNumerator);
    }

    /// @dev Set royalty fee for specific token
    /// @param _tokenId The tokenId where to add the royalty
    /// @param _receiver The royalty receiver
    /// @param _feeNumerator the fee for specific tokenId
    function setTokenRoyalty(
        uint256 _tokenId,
        address _receiver,
        uint96 _feeNumerator
    ) public onlyOwner {
        _setTokenRoyalty(_tokenId, _receiver, _feeNumerator);
    }

    /// @dev Allow owner to delete the default royalty for all collection
    function deleteDefaultRoyalty() external onlyOwner {
        _deleteDefaultRoyalty();
    }

    /// @dev Reset specific royalty
    /// @param tokenId The token id where to reset the royalty
    function resetTokenRoyalty(uint256 tokenId) external onlyOwner {
        _resetTokenRoyalty(tokenId);
    }


    // === override interface ===

    function supportsInterface(bytes4 interfaceId)
        public
        view
        virtual
        override(ERC1155, ERC2981)
        returns (bool)
    {
        return
            interfaceId == type(IERC2981).interfaceId ||
            super.supportsInterface(interfaceId);
    }
    function _msgSender() internal override view returns (address) {
        return ContextMixin.msgSender();
    }
}

