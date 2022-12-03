// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import {ERC20} from "@openzeppelin/token/ERC20/ERC20.sol";

contract MockToken is ERC20 {
    constructor(string memory name, string memory symbol) ERC20(name, symbol) {}
    
    function mint(address _to, uint256 _value) external returns (bool) {
        _mint(_to, _value);
        return true;
    }
    
    function burnFrom(address _to, uint256 _value) external returns (bool) {
        _burn(_to, _value);
        return true;
    }
}
